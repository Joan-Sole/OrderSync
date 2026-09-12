"""
OrderSync

Module:
    logger.py

Description:
    Central logging configuration for the OrderSync application.

Author:
    Joan Solé

Version:
    1.0.0
"""

from pathlib import Path
from logging.handlers import RotatingFileHandler
import logging

from core.settings import Settings


def initialise_logger(settings: Settings) -> logging.Logger:
    """
    Initialise and configure the application logger.

    Parameters
    ----------
    settings : Settings
        Application configuration.

    Returns
    -------
    logging.Logger
        Configured logger instance.
    """

    logger = logging.getLogger(settings.application.name)

    # Prevent duplicate handlers if called more than once
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    # ------------------------------------------------------------------
    # Create log directory
    # ------------------------------------------------------------------

    # script location /OrderSync/src/core/logger.py  target location /OrderSync
    project_root = Path(__file__).resolve().parents[2]

    # final target location /OrderSync/logs
    log_directory = project_root / "logs"

    log_directory.mkdir(parents=True, exist_ok=True)
    log_file = log_directory / "ordersync.log"

    # ------------------------------------------------------------------
    # Common formatter
    # ------------------------------------------------------------------

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ------------------------------------------------------------------
    # Console output
    # ------------------------------------------------------------------

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # ------------------------------------------------------------------
    # Rotating log file
    # ------------------------------------------------------------------

    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=5 * 1024 * 1024,     # 5 MB
        backupCount=5,
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # ------------------------------------------------------------------
    # Register handlers
    # ------------------------------------------------------------------

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info("======================================================")
    logger.info("%s %s",
                settings.application.name,
                settings.application.version)
    logger.info("Logger initialised.")
    logger.info("======================================================")

    return logger