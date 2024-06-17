import logging
import os
from typing import Any

GENERATOR_FILE_SEPARATOR = "_:_"
HOME_DIRECTORY = os.path.expanduser('~')
ROOT_DIRECTORY = os.path.join(HOME_DIRECTORY, 'data-toolkit')
CSV_SUFFIX = '.csv'
logger = logging.getLogger('uvicorn')

server_log = os.path.join(ROOT_DIRECTORY, "server.log")
server_access_log = os.path.join(ROOT_DIRECTORY, "server-access.log")
CUSTOM_LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s - %(name)s - %(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(asctime)s - %(name)s - %(levelprefix)s  %(client_addr)s - "%(request_line)s" %(status_code)s',
            # noqa: E501
        },
        "access_file": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '[%(asctime)s] - %(name)s - %(levelprefix)s  %(client_addr)s - "%(request_line)s" %(status_code)s',
            # noqa: E501
            "use_colors": False,
        },
    },
    "handlers": {
        "application_file_handler": {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": server_log,
            "mode": "a+",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 0,
        },
        "access_file_handler": {
            "formatter": "access_file",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": server_access_log,
            "mode": "a+",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 0,
            "encoding": "utf-8"
        },
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default", "application_file_handler"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access", "access_file_handler"], "level": "INFO", "propagate": False},
    },
}
