from __future__ import annotations

import logging
from pathlib import Path


def configure_logger(log_dir: Path) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    application_log = log_dir / "application.log"
    errors_log = log_dir / "errors.log"

    logger = logging.getLogger("employee_management_system")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        app_handler = logging.FileHandler(application_log, encoding="utf-8")
        app_handler.setLevel(logging.INFO)
        app_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        app_handler.setFormatter(app_formatter)

        error_handler = logging.FileHandler(errors_log, encoding="utf-8")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(app_formatter)

        logger.addHandler(app_handler)
        logger.addHandler(error_handler)

    logger.debug("Logger configured.")


def get_logger() -> logging.Logger:
    return logging.getLogger("employee_management_system")
