import logging
import os
import json
from datetime import datetime 
from logging.handlers import RotatingFileHandler

# Ruta del archivo de log
LOG_DIR = "logs"
LOG_FILE = "SystemOut.log"
LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

# Asegurar que el directorio exista
os.makedirs(LOG_DIR, exist_ok=True)

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage()
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        handler = RotatingFileHandler(LOG_PATH, maxBytes=5_000_000, backupCount=5)
        handler.setFormatter(JsonFormatter())
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JsonFormatter())
        logger.setLevel(getattr(logging, log_level, logging.INFO))
        logger.addHandler(handler)
        logger.addHandler(console_handler)
    return logger

# Función de conveniencia para registrar mensajes
def log(message: str):
    logger = get_logger("SystemOut")
    logger.info(message)
    
