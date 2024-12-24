# standard library imports
import os
import logging
from datetime import datetime

# third party imports
from logging.handlers import RotatingFileHandler


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configures logging settings for the application.

    Args:
        log_level: Minimum logging level (default: INFO)
    """
    # Create logs directory
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"resume_parser_{timestamp}.log")

    # Configure formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10_485_760, backupCount=5, encoding="utf-8"  # 10MB
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add handlers
    root_logger.addHandler(file_handler)

    logging.getLogger("watchfiles").setLevel(logging.WARNING)
