"""
Logging configuration for the application.
"""
import logging
import sys
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None,
    init_sentry: bool = True
) -> None:
    """
    Set up logging configuration.

    Args:
        level: Logging level (default: INFO)
        log_file: Optional file path for logging
        format_string: Optional custom format string
        init_sentry: Whether to initialize Sentry (default: True)
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure root logger
    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(format_string))
        logging.getLogger().addHandler(file_handler)

    # Initialize Sentry if requested
    if init_sentry:
        try:
            from src.utils.sentry_config import init_sentry as init_sentry_sdk
            if init_sentry_sdk():
                logging.info("Sentry initialized successfully")
        except ImportError:
            logging.warning("sentry-sdk not available, skipping Sentry initialization")
        except Exception as e:
            logging.warning(f"Failed to initialize Sentry: {e}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
