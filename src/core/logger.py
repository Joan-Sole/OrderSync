"""
OrderSync

Module:
    logger.py
    
Location:
    src\\core

Description:
    Central logging configuration for the OrderSync application.

Author:
    Joan Solé
"""

from   pathlib import Path
from   logging.handlers import RotatingFileHandler
import logging
from   core.settings import Settings


def initialise_logger(settings: Settings) -> logging.Logger:
    """
    Initialise and configure the application logging system.

    Parameters
    ----------
    settings : Settings
        Application configuration.

    Returns
    -------
    logging.Logger
        Configured root logger instance.
    """

    # Root logger. All module loggers created with
    # logging.getLogger(__name__) will inherit this configuration.
    logger = logging.getLogger()

    # Prevent duplicate handlers if called more than once.
    if logger.hasHandlers():
        return logger

    log_level = settings.application.log_level.upper()

    logger.setLevel(log_level)

    # ------------------------------------------------------------------
    # Create log directory
    # ------------------------------------------------------------------

    # script location /OrderSync/src/core/logger.py
    # target location /OrderSync
    project_root = Path(__file__).resolve().parents[2]

    # final target location /OrderSync/logs
    log_directory = project_root / settings.application.log_directory

    log_directory.mkdir(parents=True, exist_ok=True)
    log_file = log_directory / "ordersync.log"

    # ------------------------------------------------------------------
    # Common formatter
    # ------------------------------------------------------------------

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ------------------------------------------------------------------
    # Console output
    # ------------------------------------------------------------------

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # ------------------------------------------------------------------
    # Rotating log file
    # ------------------------------------------------------------------

    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=5 * 1024 * 1024,     # 5 MB
        backupCount=5,
        encoding="utf-8",
    )

    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    # ------------------------------------------------------------------
    # Register handlers
    # ------------------------------------------------------------------

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info("======================================================")
    logger.info(
        "%s %s",
        settings.application.name,
        settings.application.version,
    )
    logger.info("Logger initialised.")
    logger.info("======================================================")

    return logger