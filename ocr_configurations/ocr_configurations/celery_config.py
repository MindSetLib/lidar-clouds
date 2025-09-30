"""Настройка конфигурации Celery."""
from .config import Config

from celery import Celery
from kombu import Exchange, Queue

# Общий exchange — все очереди используют один direct exchange
default_exchange = Exchange('celery', type='direct')


def make_queue(name):
    return Queue(
        name,
        exchange=default_exchange,           # Exchange, по которому задачи попадают в очередь
        routing_key=name,                    # Routing key, совпадает с именем очереди
        durable=True,                        # Сохранять очередь при перезапуске RabbitMQ
        auto_delete=False,                   # Не удалять очередь при отсутствии подписчиков
        exclusive=False,                     # Очередь не будет уничтожена при завершении соединения
        queue_arguments={
            'x-queue-mode': 'lazy'           # Ленивая очередь: задачи сразу пишутся на диск (экономия RAM)
        }
    )


# Явное определение всех очередей, которые используются в приложении
task_queues = [
    make_queue('downloader'),
    make_queue('convertor'),
    make_queue('classification'),
    make_queue('claim'),
    make_queue('claim-surya'),
    make_queue('bank_details'),
    make_queue('passport'),
    make_queue('insurance_application'),
    make_queue('combiner'),
]

# Инициализация объекта Celery
CELERY = Celery(
    'tasks',                           # Название приложения
    backend=None,          # Backend для хранения результатов выполнения задач
    broker=Config.BROKER_URL,          # Брокер сообщений (например, RabbitMQ)
)

# Регистрация очередей
CELERY.conf.task_queues = task_queues

# Настройки по умолчанию (если не указано иное)
CELERY.conf.task_default_exchange = 'celery'         # Exchange по умолчанию
CELERY.conf.task_default_exchange_type = 'direct'    # Тип exchange (direct → по routing_key)
CELERY.conf.task_default_routing_key = 'default'     # routing_key по умолчанию

# Основные настройки Celery
CELERY.conf.update(
    worker_prefetch_multiplier=1,             # Сколько задач может захватить воркер заранее
    task_acks_late=True,                      # Задачи подтверждаются (ACK) только после выполнения
    task_reject_on_worker_lost=True,          # Повтор задачи при падении воркера
    broker_pool_limit=None,                   # Без ограничения на количество соединений к брокеру
    broker_connection_retry_on_startup=True,  # Повторные попытки подключения к брокеру при старте
    socket_keepalive=True,                    # Пинговать сокет, чтобы не терять соединение
    worker_send_task_events=True,             # Отправка событий выполнения воркером (для мониторинга)
    task_send_sent_event=True,                # Отправка события при отправке задачи (для мониторинга)
    task_time_limit=1200,                     # Жёсткий лимит выполнения задачи (60 сек * 20 мин = 1200)
                                              # Не работает при pool=solo
    task_soft_time_limit=900,                 # Мягкий лимит (возбуждает исключение SoftTimeLimitExceeded)
                                              # Не работает при pool=solo
    result_backend=None,                      # Не сохранять результаты задач в Redis
)

# Настройки транспортного уровня брокера (RabbitMQ)
CELERY.conf.broker_transport_options = {
    'visibility_timeout': 3600,               # Таймаут перед повторной доставкой невыполненной задачи
    'retry_policy': {                         # Политика переподключений к брокеру
        'timeout': 5,                         # Таймаут между попытками (сек)
        'max_retries': 90,                    # Максимальное количество попыток
        'interval_start': 0,                  # Начальный интервал между попытками
        'interval_step': 0.5,                 # Шаг увеличения интервала
        'interval_max': 6,                    # Максимальный интервал между попытками
    },
    'socket_timeout': 5,                      # Таймаут для операций с сокетом (чтение/запись) (включая confirm)
    'socket_connect_timeout': 2,              # Таймаут на установку соединения с брокером
    'redis_socket_connect_timeout': 2.0,      # Таймаут подключения к Redis (если Redis используется как брокер)
    "confirm_publish": True,                  # Ждать подтверждения от брокера, что задача поставлена в очередь
}