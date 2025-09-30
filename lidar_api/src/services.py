from typing import Optional
from pathlib import Path
from ocr_configurations import Config, setup_logging
from fastapi import FastAPI, UploadFile


logger = setup_logging()


class PCDService:
    """Работа с загрузкой PCD и постановкой в очередь."""

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir

    def save_file(self, file: UploadFile, uid: str) -> str:
        """Сохраняем файл и возвращаем путь."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{uid}.pcd"
        filepath = self.storage_dir / filename
        with open(filepath, "wb") as f:
            f.write(file.file.read())
        logger.info("Файл сохранен: %s", filepath)
        return str(filepath)

    def enqueue(self, file_path: str, uid: str):
        """Отправка задачи в очередь (имитация)."""
        # TODO: celery_app.send_task("detector.process", args=[file_path, uid])
        logger.info("Файл %s отправлен в очередь", file_path)

    def set_status(self, uid: str, status: str):
        rds.set(uid, status)

    def get_status(self, uid: str) -> Optional[str]:
        return rds.get(uid)