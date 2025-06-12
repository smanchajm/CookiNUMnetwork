"""
Logging configuration module.
Handles the setup and configuration of the application's logging system.
"""

import logging
from src.utils.resource_manager import ResourceManager

# Logging configuration
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(levelname)s - %(message)s"
LOG_DIR = ResourceManager.get_app_data_paths("logs")
LOG_FILE = LOG_DIR / "cookinum.log"


def setup_logging():
    """
    Configure the application's logging system.
    Creates the logs directory if it doesn't exist and sets up file and console handlers.
    """
    # Create logs directory if it doesn't exist
    # LOG_DIR.mkdir(exist_ok=True)
    print(LOG_DIR)
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
    )

    # Create and return logger
    logger = logging.getLogger("CookiNUM")
    return logger


# Initialize logger
logger = setup_logging()
