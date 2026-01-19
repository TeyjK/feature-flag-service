import logging
import json
import sys
from datetime import datetime

class JsonFormatter(logging.Formatter):
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        if hasattr(record, 'context'):
            log_data['context'] = record.context
            
        return json.dumps(log_data)

def setup_logging():
    logger = logging.getLogger("feature_flags")
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    
    logger.addHandler(handler)
    
    return logger