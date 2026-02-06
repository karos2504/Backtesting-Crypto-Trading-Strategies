import logging
import os
import sys
from common.config import LOGS_DIR

def setup_logging(name: str = 'app', log_file: str = 'app.log', level=logging.INFO):
    """
    Setup logging configuration.
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG) # Capture all, handlers will filter

    # Avoid duplicate handlers/logs if setup is called multiple times
    if logger.hasHandlers():
        return logger

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File Handler
    file_path = os.path.join(LOGS_DIR, log_file)
    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
