import logging
import logging.config


logging_config = {
    "version": 1,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "verbose"
        }
    },
    "loggers": {
        "app_logger": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG"
    }
}


def setup_logging(logger_name="app_logger") -> logging.Logger:
    """
    Настраивает логирование и возвращает логгер с заданным именем.

    :param logger_name: Имя логгера. По умолчанию "app_logger".
    :return: Настроенный логгер.
    """
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger(logger_name)
    return logger
