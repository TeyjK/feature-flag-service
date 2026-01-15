import redis.asyncio as redis

from app.config import settings

redis_pool = None
redis_client = None

async def init_redis():
    global redis_pool
    global redis_client

    redis_pool = redis.ConnectionPool.from_url(
        settings.redis_url,
        max_connections=settings.redis_pool_max,
        decode_responses=True
    )

    redis_client = redis.Redis(connection_pool=redis_pool)

async def close_redis():
    global redis_pool
    global redis_client

    await redis_client.aclose()
    await redis_pool.disconnect()