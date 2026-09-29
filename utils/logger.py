"""Logging utility for Bot Orchestration"""

import logging
import os
from logging.handlers import RotatingFileHandler
from orchestrator.config import LOG_LEVEL, LOG_DIR, LOG_FORMAT


def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """
    Setup logger for a bot or component
    
    Args:
        name: Logger name
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        os.makedirs(LOG_DIR, exist_ok=True)
        file_path = os.path.join(LOG_DIR, log_file)
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(LOG_LEVEL)
        file_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)
    
    return logger
