import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    """Base application configs."""

    BASE_DIR = os.environ.get("BASE_DIR", os.getcwd())
    IMG_STORAGE = os.path.join(BASE_DIR, 'file_storage')
    TEST_FILES_STORAGE = os.path.join(BASE_DIR, 'test_storage')

    # Настройки очереди
    REDIS_URL = os.environ.get('REDIS_URL')
    BROKER_URL = os.environ.get('BROKER_URL')

    # DB
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    DB_ECHO = False

    # БД в Redis
    REDIS_HOST = os.environ.get('REDIS_HOST')
    REDIS_PORT = os.environ.get('REDIS_PORT')
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    REDIS_DB = os.environ.get('REDIS_DB')
    # Допустимое время просрочки записи в редис в днях
    DAY_TIMEOUT = 1

    # Актуальность созданных директорий в днях
    DIR_REV_DAY = 1

    # Конфигурация повторов выполнения задач
    # Количество попыток
    COUNT_ATTEMPTS = int(os.environ.get('COUNT_ATTEMPTS'))
    # Стартовый таймаут, секунд
    COUNTDOWN = int(os.environ.get('COUNTDOWN'))
    # Максимальный таймаут, секунд
    MAX_TIMEOUT_RETRY = int(os.environ.get('MAX_TIMEOUT_RETRY'))

    # Токен для ограничения доступа к api
    SECRET_TOKEN = os.environ.get('SECRET_TOKEN')

    # Количество одновременных асинхронных задач
    # - сколько параллельных скачиваний возможно
    CONCURRENT_TASKS = 5
    # Время ожидания ответа на запрос с внешнего апи, секунд
    HTTP_TIMEOUT = 60


    # S3 Хранилище - скачивание весов моделей
    S3_ACCESS_KEY_ID = os.environ.get('S3_ACCESS_KEY_ID')
    S3_SECRET_ACCESS_KEY = os.environ.get('S3_SECRET_ACCESS_KEY')
    S3_ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL')
