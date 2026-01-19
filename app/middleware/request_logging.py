import logging
import time
from fastapi import Request

logger = logging.getLogger("feature_flags")

async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration_ms = (time.time() - start_time) * 1000
    
    logger.info("API request completed", extra = {
        'context': {
            'method': request.method,
            'path': request.url.path,
            'status_code': response.status_code,
            'duration_ms': round(duration_ms, 2)
        }
    })
    
    return response