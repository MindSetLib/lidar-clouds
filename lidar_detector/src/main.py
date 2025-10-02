import os
from typing import Optional


from ocr_configurations import setup_logging
from ocr_configurations import CELERY
from ocr_configurations import CelerySender, CeleryTaskParams, Config

from kombu.exceptions import OperationalError as KombuOE
from redis.exceptions import ConnectionError
from sqlalchemy.exc import OperationalError as SqlalchemyOE

from OpenPCDet.run_full_pipeline import main

import redis

logger = setup_logging()

CELERY.conf.update(
    broker_heartbeat=None
)


rds = redis.from_url(Config.REDIS_URL, decode_responses=True)


def get_status(uid: str) -> Optional[dict]:
    data = rds.hgetall(uid)
    return data or None


def update_status_files(uid: str, result_filename: str,
                        boxes_json_filename: str, status: str,
                        comment) -> bool:
    data = get_status(uid)
    if not data:
        return False  # ключ не найден
    data["result_filename"] = result_filename
    data["boxes_json_filename"] = boxes_json_filename
    data["status"] = status
    data["comment"] = comment
    rds.hset(uid, mapping=data)
    return True


@CELERY.task(
    bind=True,
    name='get_lidar_boxes',
    ignore_result=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=Config.COUNT_ATTEMPTS,
)
def get_lidar_boxes(task_self, **kwargs) -> bool:
    """Celery-задача для распознавания банковских данных."""
    uid_request = kwargs.get('uid_request')
    
    comment = "Файл в обработке у детектора"
    update_status_files(uid_request, "", "", "processing", comment)
    
    file_name = kwargs.get('files')[0]
    img_storage = Config.IMG_STORAGE
    logger.info('%s - Передаю файл на обработку детектору: %s', uid_request, file_name)
    predict = main(img_storage, file_name)
    
    result_filename = predict.get("result_filename")
    boxes_json_filename = predict.get("boxes_json_filename")
    logger.info('%s - Обновляю запись в Redis: %s', uid_request, predict)
    
    # result_filename = "prpoba.pcd"
    # boxes_json_filename = "proba.json"
    
    status = 'ready'
    comment = "Файл обработан детектором"

    update_status_files(
        uid_request,
        result_filename,
        boxes_json_filename,
        status,
        comment,
    )
