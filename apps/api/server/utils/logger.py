import logging
import json
import datetime
from flask import request, has_request_context

# ------------------------------------------------------

class JsonFormatter(logging.Formatter):
    """
    Custom formatter to output logs in JSON format.
    Includes request metadata if available.
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "funcName": record.funcName,
            "line": record.lineno,
        }

        # Include extra attributes passed to the logger
        if hasattr(record, "extra_info"):
            log_record["extra_info"] = record.extra_info

        # Include request context if available
        if has_request_context():
            log_record["request"] = {
                "method": request.method,
                "url": request.url,
                "remote_addr": request.remote_addr,
                "path": request.path,
            }

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)

def setup_logger(name="kurudu"):
    """
    Initializes a logger with the JsonFormatter.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if setup_logger is called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        
        # Prevent propagation to the root logger to avoid duplicate logs in some environments
        logger.propagate = False

    return logger

# Global logger instance
logger = setup_logger()
