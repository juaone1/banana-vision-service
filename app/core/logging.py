import logging
import sys
from typing import Any, Dict
from pathlib import Path
from logging.handlers import RotatingFileHandler
from fastapi.logger import logger as fastapi_logger

from app.core.config import settings

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
JSON_LOG_FORMAT = {
    "timestamp": "%(asctime)s",
    "name": "%(name)s",
    "level": "%(levelname)s",
    "message": "%(message)s",
}

def setup_logger(name: str, log_file: str | None = None) -> logging.Logger:
    """
    Set up a logger with both console and file handlers.
    
    Args:
        name: The name of the logger
        log_file: Optional file path for logging
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)

    # File handler (if log_file is provided)
    if log_file:
        file_handler = RotatingFileHandler(
            LOGS_DIR / log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(file_handler)

    return logger

# Create loggers for different components
loggers = {
    # Core application logger
    'app': setup_logger("banana_vision", "app.log"),
    
    # API component loggers
    'api': setup_logger("banana_vision.api", "api.log"),
    
    # Database operations logger
    'db': setup_logger("banana_vision.db", "db.log"),
    
    # Authentication and authorization logger
    'auth': setup_logger("banana_vision.auth", "auth.log"),
    
    # Background tasks logger
    'tasks': setup_logger("banana_vision.tasks", "tasks.log")
}

# Integrate with FastAPI logger
fastapi_logger.handlers = loggers['app'].handlers

def get_logger(component: str = 'app') -> logging.Logger:
    """
    Get a logger for a specific component.
    
    Args:
        component: The component name ('app', 'api', 'db', 'auth', 'tasks')
    
    Returns:
        logging.Logger: The requested logger
    """
    return loggers.get(component, loggers['app'])