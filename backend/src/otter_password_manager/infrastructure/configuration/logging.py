import json
import logging
import logging.config
from datetime import UTC, datetime

from otter_password_manager.infrastructure.configuration.settings import Settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(settings: Settings) -> None:
    formatter = "json" if settings.log_format == "json" else "console"
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
                },
                "json": {"()": JsonFormatter},
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": formatter,
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {"handlers": ["default"], "level": settings.log_level.upper()},
            "loggers": {
                "uvicorn": {"handlers": ["default"], "propagate": False},
                "uvicorn.error": {"handlers": ["default"], "propagate": False},
                "uvicorn.access": {"handlers": ["default"], "propagate": False},
            },
        }
    )

