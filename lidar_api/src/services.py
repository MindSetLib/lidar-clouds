from typing import List, Optional
from pathlib import Path
from ocr_configurations import CelerySender, CeleryTaskParams, setup_logging
from fastapi import UploadFile
import redis
import json


logger = setup_logging()


def send_to_detector(
        uid_request: str,
        files: List[str]):
    """Отправить задачу на модель детекции."""

    task_kwargs = {
        'uid_request': uid_request,
        'files': files,
    }
    queue_params = CeleryTaskParams(
        queue_name='detector',
        task_name='get_lidar_boxes',
        kwargs=task_kwargs,
    )
    task_id = CelerySender().send_to_queue(queue_params)
    return task_id


class PCDService:
    """Работа с загрузкой PCD и постановкой в очередь."""

    def __init__(self, storage_dir: Path, rds: redis.Redis):
        self.storage_dir = storage_dir
        self.rds = rds

    def save_file(self, file: UploadFile, uid: str) -> str:
        """Сохраняем файл и возвращаем путь."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{uid}.pcd"
        filepath = self.storage_dir / filename
        with open(filepath, "wb") as f:
            f.write(file.file.read())
        logger.info("Файл сохранен: %s", filepath)
        return str(filename)

    def enqueue(self, file_path: str, uid: str):
        """Отправка задачи в очередь (имитация)."""
        send_to_detector(
            uid_request=uid,
            files=[file_path],)
        logger.info("Файл %s на детектор", file_path)

    def set_status(
        self,
        uid: str,
        status: str,
        src_filename: str,
        result_filename: str | None = None,
        boxes: list | None = None
    ):
        """Сохраняем все данные одним хэшем."""
        value = {
            "src_filename": src_filename,
            "status": status,
            "comment": "Файл отправлен на детектор",
            "result_filename": result_filename or "",
            "boxes_json_filename": "",
            "boxes": json.dumps(boxes or []),
        }
        self.rds.hset(uid, mapping=value)

    def get_status(self, uid: str) -> Optional[dict]:
        data = self.rds.hgetall(uid)
        return data or None
