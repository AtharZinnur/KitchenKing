"""
Logging configuration for Pic2Kitchen application
"""
import logging
import os
from datetime import datetime

def setup_logger(name, log_file=None, level=logging.INFO):
    """Setup a logger with file and console handlers"""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Create application-wide logger
app_logger = setup_logger('pic2kitchen', 
                         log_file=f'logs/pic2kitchen_{datetime.now().strftime("%Y%m%d")}.log')