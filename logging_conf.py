# app/logging_conf.py
import logging.config
from pathlib import Path

def setup_logging(log_dir: str = "logs"):
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            },
            "access": {
                "format": "%(asctime)s | ACCESS | %(message)s"
            },
            "raw": {
                "format": "%(asctime)s | %(message)s"
            },
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "app_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{log_dir}/app.log",
                "maxBytes": 5_000_000,
                "backupCount": 5,
                "formatter": "default",
                "encoding": "utf-8",
            },
            "access_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{log_dir}/access.log",
                "maxBytes": 5_000_000,
                "backupCount": 5,
                "formatter": "access",
                "encoding": "utf-8",
            },
            "llm_raw_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{log_dir}/llm_raw.log",
                "maxBytes": 20_000_000,
                "backupCount": 10,
                "formatter": "raw",
                "encoding": "utf-8",
            },
        },

        "loggers": {
            # 네 앱 코드에서 쓰는 로거
            "psano": {
                "level": "INFO",
                "handlers": ["console", "app_file"],
                "propagate": False,
            },
            # 커스텀 access 로거
            "psano.access": {
                "level": "INFO",
                "handlers": ["access_file"],
                "propagate": False,
            },
            "psano.llm_raw": {
                "level": "INFO",
                "handlers": ["llm_raw_file"],
                "propagate": False,
            },
            # uvicorn 기본 access log는 꺼버림
            "uvicorn.access": {
                "level": "WARNING",
                "handlers": [],
                "propagate": False,
            },
            # uvicorn error는 그냥 둠(콘솔로 뜸)
            "uvicorn.error": {"level": "INFO"},
        },
    }

    logging.config.dictConfig(LOGGING)
