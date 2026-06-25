import logging
import json
import uuid
from datetime import datetime
from contextvars import ContextVar

# Context variable to store request ID across the async event loop
request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="")

class JSONLogFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "request_id": request_id_ctx_var.get(),
        }
        
        # Include exception info if present
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONLogFormatter())
    logger.addHandler(console_handler)
