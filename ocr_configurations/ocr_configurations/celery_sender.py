import logging

from dataclasses import dataclass
from datetime import datetime
from time import sleep, time
from typing import Any, Dict, List, Optional, Tuple

from .celery_config import CELERY

from celery.app.control import Inspect
from celery.exceptions import TimeoutError


logger = logging.getLogger("app_logger")


@dataclass
class CeleryTaskParams:
    """Prediction dataclass."""
    task_name: str
    queue_name: str
    kwargs: Dict[str, Any]
    args: Tuple[Any, ...] = ()


class CelerySender:
    """Отправитель задач в очереди."""
    def send_to_queue(self, params: CeleryTaskParams) -> str:
        """Отправить задачу в очередь."""
        start = datetime.now()
        params.kwargs.setdefault('start', start)

        result = CELERY.send_task(
            params.task_name,
            args=(*params.args,),
            kwargs=params.kwargs,
            queue=params.queue_name,
            retry=True,  # в случае временных сбоев соединения с брокером сообщений.
            retry_policy={
                'max_retries': 5,
                'interval_start': 0.1,
                'interval_step': 0.5,
                'interval_max': 2,
            }
        )

        return result.id

    @staticmethod
    def send_healthcheck(worker_queue: str):
        """Отправить проверочную задачу в очередь."""
        result = CELERY.send_task(
            'celery_worker.healthcker',
            priority=10,
            queue=worker_queue,
            reply_to='result_queue',
            wait=True,
        )
        return result.id

    @staticmethod
    def check_task_status(task_id, timeout=10):
        """Проверить статус задачи."""
        start_time = time()
        while time() - start_time < timeout:
            result = CELERY.AsyncResult(task_id)
            if result.ready():
                return result.get()
            sleep(0.5)
        return False


class CeleryInspector:
    """Инспектор состояния воркеров и очередей Celery"""
    def __init__(self):
        self.inspector = None

    def create_inspector(self, timeout: float = 5.0) -> Inspect:
        """Получить инспектора воркеров и очередей Celery"""
        if not self.inspector:
            self.inspector = CELERY.control.inspect(timeout=timeout)
        return self.inspector

    def are_workers_online(self) -> bool:
        """
        Проверяет, что хотя бы один воркер подключен к брокеру.
        Args:
            timeout: Максимальное время ожидания ответа (в секундах)
        Returns:
            bool: True если хотя бы один воркер ответил
        """
        self.create_inspector()
        try:
            response = self.inspector.ping()
        except TimeoutError:
            logger.warning("Workers did not respond to ping within timeout")
            return False
        except Exception:
            logger.exception("Worker ping failed")
            return False

        if response and isinstance(response, dict):
            return len(response) > 0
        return False

    def get_worker_queues(self) -> Optional[Dict[str, Any]]:
        """Получить список активных очередей обслуживаемых воркерами"""
        self.create_inspector()
        try:
            worker_queues = self.inspector.active_queues()
        except TimeoutError:
            logger.warning("Workers did not respond to ping within timeout")
            return
        except Exception:
            logger.exception("Queue-specific worker check failed")
            return
        return worker_queues
