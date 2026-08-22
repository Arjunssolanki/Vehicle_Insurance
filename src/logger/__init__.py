import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Constants for log configuration
LOG_DIR = 'logs'
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3  # Number of backup log files to keep

# Robust Path Tracking: Calculates the path relative to this file's physical location
# __file__ = D:\2026\newstudy\Vehicle_Insurance\src\logger\__init__.py
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # Points to src/logger
SRC_DIR = os.path.dirname(CURRENT_DIR)                    # Points to src
PROJECT_ROOT = os.path.dirname(SRC_DIR)                   # Points to Vehicle_Insurance

# Create the folder explicitly inside your project workspace
log_dir_path = os.path.join(PROJECT_ROOT, LOG_DIR)
os.makedirs(log_dir_path, exist_ok=True)
log_file_path = os.path.join(log_dir_path, LOG_FILE)

def configure_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    if not logger.handlers:
        formatter = logging.Formatter("[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s")

        # File handler with rotation
        file_handler = RotatingFileHandler(log_file_path, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

configure_logger()
