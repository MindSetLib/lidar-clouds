import os


from ocr_configurations import setup_logging
from ocr_configurations import CELERY
from ocr_configurations import CelerySender, CeleryTaskParams, Config

from kombu.exceptions import OperationalError as KombuOE
from redis.exceptions import ConnectionError
from sqlalchemy.exc import OperationalError as SqlalchemyOE



logger = setup_logging()


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
    from pprint import pprint
    logger.info("Start task %s", task_self.request.id)
    logger.info("Task params:")
    pprint(kwargs)
