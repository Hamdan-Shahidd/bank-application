"""
This file sets up structured logging, It sends log messages to both terminal and log file,
and automatically rotates the log file when it get's to large. 
"""

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler # Write logs to a file automatically and make a new file if the file gets large. 

# Creates the log directory in the root directory. 
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configuring our application's loger.
def setup_logging():
    # Creates or retrives the logger named bankapp. Than we can use it as logger.info, logger.warning, logger.error
    logger = logging.getLogger("bankapp")
    """
    Set the logging level. in python the logging levels go by
    DEBUG -> INFO -> WARNING -> ERROR -> CRITICAL
    So by INFO we only get info and more critcal ones such as warning, error and critical.
    """
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger  # already configured, avoid duplicate handlers on reload

    # Formats the log message 
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console output — This creates handler that sends logs to the console/terminal. 
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File output — This creates handler that write logs in the file. This is a rotateable file and can grow to 5 MB max
    file_handler = RotatingFileHandler(
        LOG_DIR / "bankapp.log",
        maxBytes=5_000_000,   # 5 MB per file
        backupCount=3,        # keep 3 old files before deleting the oldest
    )
    # Add the formatter to the file handler.
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()