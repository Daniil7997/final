import logging
import sys
from logging.handlers import RotatingFileHandler

file_handler = RotatingFileHandler(
    filename="team_management.log",
    mode="a",
    encoding="utf-8",
    maxBytes=5 * 1024 * 1024,
)
console_handler = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

loggers = (
    "uvicorn",
    "uvicorn.access",
    "uvicorn.error",
    "gunicorn",
    "gunicorn.access",
    "gunicorn.error",
    "fastapi",
)

for logger_name in loggers:
    logger = logging.getLogger(logger_name)
    logger.handlers = []
    logger.propagate = False
    # logger.disabled = True
