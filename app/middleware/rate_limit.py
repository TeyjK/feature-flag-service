import time
from app import cache
from fastapi import HTTPException

async def check_rate_limit(key_id: str, rate_limit: int) -> dict:
    current_window = int(time.time() // 60)
    rate_limit_key = f"ratelimit:{key_id}:{current_window}"
    count = await cache.redis_client.incr(rate_limit_key)
    if count == 1:
        await cache.redis_client.expire(rate_limit_key, 60)
    if count > rate_limit:
        raise HTTPException(status_code = 429, detail = "Rate limit exceeded")
    return {
        "limit": rate_limit,
        "remaining": max(0, rate_limit - count),
        "reset": (current_window + 1) * 60
    }
