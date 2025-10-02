"""
Logging utilities for the YouTube Comment Scraper.

This module provides centralized logging configuration and setup.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

# Handle imports for both package and direct execution
try:
    from .config import ConfigManager
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.append(str(Path(__file__).parent))
    from config import ConfigManager


def setup_logger(
    name: str = "youtube_scraper",
    config_manager: Optional[ConfigManager] = None,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with both file and console handlers.
    
    Args:
        name: Logger name
        config_manager: Configuration manager instance
        log_level: Logging level (overrides config)
        log_file: Log file path (overrides config)
        
    Returns:
        Configured logger instance
    """
    # Initialize config manager if not provided
    if config_manager is None:
        config_manager = ConfigManager()
    
    # Get logging configuration
    logging_config = config_manager.get_logging_config()
    
    # Determine log level
    level = log_level or logging_config.get('level', 'INFO')
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Determine log file path
    if log_file is None:
        log_file = logging_config.get('log_file', 'logs/scraper.log')
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    max_size_mb = logging_config.get('max_log_size_mb', 10)
    backup_count = logging_config.get('backup_count', 5)
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_size_mb * 1024 * 1024,  # Convert MB to bytes
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = "youtube_scraper") -> logging.Logger:
    """
    Get an existing logger or create a new one.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set it up
    if not logger.handlers:
        return setup_logger(name)
    
    return logger


class LoggerMixin:
    """
    Mixin class that provides logging capabilities to other classes.
    
    Usage:
        class MyClass(LoggerMixin):
            def my_method(self):
                self.logger.info("This is a log message")
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = None
    
    @property
    def logger(self) -> logging.Logger:
        """Get the logger for this class."""
        if self._logger is None:
            class_name = self.__class__.__name__
            self._logger = get_logger(f"youtube_scraper.{class_name}")
        return self._logger


def log_function_call(func):
    """
    Decorator to log function calls with parameters and execution time.
    
    Usage:
        @log_function_call
        def my_function(param1, param2):
            return result
    """
    def wrapper(*args, **kwargs):
        logger = get_logger()
        func_name = func.__name__
        
        # Log function entry
        logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")
        
        try:
            import time
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            # Log successful completion
            execution_time = end_time - start_time
            logger.debug(f"{func_name} completed successfully in {execution_time:.3f}s")
            
            return result
            
        except Exception as e:
            # Log exception
            logger.error(f"{func_name} failed with error: {str(e)}", exc_info=True)
            raise
    
    return wrapper


def log_api_call(service: str, method: str, params: dict = None):
    """
    Log API calls for monitoring and debugging.
    
    Args:
        service: Service name (e.g., 'YouTube API')
        method: API method name
        params: API parameters (sensitive data will be masked)
    """
    logger = get_logger()
    
    # Mask sensitive parameters
    safe_params = {}
    if params:
        for key, value in params.items():
            if 'key' in key.lower() or 'token' in key.lower() or 'secret' in key.lower():
                safe_params[key] = '***MASKED***'
            else:
                safe_params[key] = value
    
    logger.info(f"API Call - {service}.{method} with params: {safe_params}")


# Configure root logger to prevent duplicate messages
logging.getLogger().setLevel(logging.WARNING)
