import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_FILE = Path(__file__).parent.parent / "app.log"
_FMT = "[%(asctime)s] [%(levelname)s] in %(module)s: %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str = "followspyv") -> logging.Logger:
    """Return a named logger configured with console + rolling file handlers.

    Safe to call multiple times — handlers are only attached once.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(_FMT, datefmt=_DATE_FMT)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Rolling file handler: 5 MB per file, keep 3 backups
    file_handler = RotatingFileHandler(
        _LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
