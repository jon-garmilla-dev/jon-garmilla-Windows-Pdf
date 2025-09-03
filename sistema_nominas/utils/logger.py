"""
Sistema de logging centralizado para la aplicación de nóminas.
"""
import logging
import os
import time
from datetime import datetime


class NominaLogger:
    """Logger centralizado para la aplicación."""
    
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
        """Configura el logger con archivos rotatorios."""
        # Crear directorio de logs
        logs_dir = 'logs'
        os.makedirs(logs_dir, exist_ok=True)

        # Limpiar logs antiguos
        self._limpiar_logs_antiguos(logs_dir)
        
        # Timestamp para el archivo actual
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(logs_dir, f'nominas_{timestamp}.log')
        
        # Configurar logger
        self._logger = logging.getLogger('nominas_app')
        self._logger.setLevel(logging.DEBUG)
        
        # Evitar duplicar handlers
        if not self._logger.handlers:
            # Handler para archivo
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # Handler para consola
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Formato detallado
            formatter = logging.Formatter(
                '%(asctime)s - [%(levelname)8s] - '
                '%(funcName)s:%(lineno)d - %(message)s'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)
    
    def get_logger(self):
        """Retorna el logger configurado."""
        return self._logger

    def _limpiar_logs_antiguos(self, logs_dir, dias_a_mantener=7):
        """Elimina archivos de log más antiguos que un número de días."""
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


# Instancia global del logger
logger = NominaLogger()


def get_logger():
    """Función helper para obtener el logger desde cualquier módulo."""
    return logger.get_logger()


def log_info(message, *args, **kwargs):
    """Helper function para logging info."""
    logger.info(message, *args, **kwargs)


def log_debug(message, *args, **kwargs):
    """Helper function para logging debug.""" 
    logger.debug(message, *args, **kwargs)


def log_warning(message, *args, **kwargs):
    """Helper function para logging warning."""
    logger.warning(message, *args, **kwargs)


def log_error(message, *args, **kwargs):
    """Helper function para logging error."""
    logger.error(message, *args, **kwargs)


def log_critical(message, *args, **kwargs):
    """Helper function para logging critical."""
    logger.critical(message, *args, **kwargs)
