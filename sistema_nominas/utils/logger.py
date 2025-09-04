"""
Centralized logging system for the payroll application.

Provides structured logging with automatic file rotation, console output,
and log cleanup for enterprise payroll processing operations.
"""
import logging
import os
import time
from datetime import datetime


class NominaLogger:
    """Centralized logger for the payroll application.
    
    Implements singleton pattern to ensure consistent logging across all modules.
    Automatically manages log files with rotation and cleanup based on retention policy.
    """
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self):
        """Configure logger with rotating file handlers.
        
        Creates log directory, cleans up old logs, and sets up both file and console
        handlers with appropriate formatting and log levels.
        """
        # Create logs directory if it doesn't exist
        logs_dir = 'logs'
        os.makedirs(logs_dir, exist_ok=True)

        # Clean up old log files based on retention policy
        self._limpiar_logs_antiguos(logs_dir)
        
        # Generate timestamp for current log file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(logs_dir, f'nominas_{timestamp}.log')
        
        # Configure main logger instance
        self._logger = logging.getLogger('nominas_app')
        self._logger.setLevel(logging.DEBUG)
        
        # Avoid duplicate handlers on multiple initializations
        if not self._logger.handlers:
            # File handler for persistent logging
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # Console handler for real-time monitoring
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Detailed formatting with timestamp and source location
            formatter = logging.Formatter(
                '%(asctime)s - [%(levelname)8s] - '
                '%(funcName)s:%(lineno)d - %(message)s'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)
    
    def get_logger(self):
        """Return the configured logger instance.
        
        Returns:
            logging.Logger: Configured logger with file and console handlers
        """
        return self._logger

    def _limpiar_logs_antiguos(self, logs_dir, dias_a_mantener=60):
        """Remove log files older than specified number of days.
        
        Default retention is 60 days (2 months) for monthly payroll operations.
        This allows reviewing previous month's logs in case of issues.
        
        Args:
            logs_dir (str): Directory containing log files
            dias_a_mantener (int): Number of days to retain logs
        """
        try:
            limite_segundos = dias_a_mantener * 24 * 60 * 60
            limite_tiempo = time.time() - limite_segundos
            for filename in os.listdir(logs_dir):
                if not (filename.startswith('nominas_') and
                        filename.endswith('.log')):
                    continue

                file_path = os.path.join(logs_dir, filename)
                if os.path.isfile(file_path):
                    if os.path.getmtime(file_path) < limite_tiempo:
                        os.remove(file_path)
                        self.info(f"Log antiguo eliminado: {filename}")
        except OSError as e:
            self.error(f"Error al limpiar logs antiguos: {e}")
    
    def info(self, message, *args, **kwargs):
        """Log level info."""
        self._logger.info(message, *args, **kwargs)
    
    def debug(self, message, *args, **kwargs):
        """Log level debug."""
        self._logger.debug(message, *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        """Log level warning."""
        self._logger.warning(message, *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        """Log level error."""
        self._logger.error(message, *args, **kwargs)
    
    def critical(self, message, *args, **kwargs):
        """Log level critical."""
        self._logger.critical(message, *args, **kwargs)


# Global logger instance for application-wide access
logger = NominaLogger()


def get_logger():
    """Helper function to get logger from any module.
    
    Returns:
        logging.Logger: Application logger instance
    """
    return logger.get_logger()


def log_info(message, *args, **kwargs):
    """Helper function for info level logging.
    
    Args:
        message (str): Log message
        *args: Additional arguments for message formatting
        **kwargs: Additional keyword arguments for logger
    """
    logger.info(message, *args, **kwargs)


def log_debug(message, *args, **kwargs):
    """Helper function for debug level logging.
    
    Args:
        message (str): Log message
        *args: Additional arguments for message formatting
        **kwargs: Additional keyword arguments for logger
    """
    logger.debug(message, *args, **kwargs)


def log_warning(message, *args, **kwargs):
    """Helper function for warning level logging.
    
    Args:
        message (str): Log message
        *args: Additional arguments for message formatting
        **kwargs: Additional keyword arguments for logger
    """
    logger.warning(message, *args, **kwargs)


def log_error(message, *args, **kwargs):
    """Helper function for error level logging.
    
    Args:
        message (str): Log message
        *args: Additional arguments for message formatting
        **kwargs: Additional keyword arguments for logger
    """
    logger.error(message, *args, **kwargs)


def log_critical(message, *args, **kwargs):
    """Helper function for critical level logging.
    
    Args:
        message (str): Log message
        *args: Additional arguments for message formatting
        **kwargs: Additional keyword arguments for logger
    """
    logger.critical(message, *args, **kwargs)
