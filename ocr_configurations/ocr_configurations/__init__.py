"""Модуль конфигураций для работы с сервисом распознавания документов OCR."""
from .config import Config
from .celery_config import CELERY
from .celery_sender import CelerySender, CeleryTaskParams
from .logger import setup_logging


__all__ = [
    'Config',
    'CELERY',
    'CelerySender',
    'CeleryTaskParams',
    'setup_logging',
]
