import redis.asyncio as redis
from app.config import settings
import orjson
from typing import Optional

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

async def get_flag_from_cache(flag_id: str) -> Optional[dict]:
    flag = await redis_client.get(f"flag:{flag_id}")
    if flag:
        return orjson.loads(flag)
    return None

def serialize_flag(flag_data: dict) -> str:
    flag_copy = dict(flag_data)
    if 'created_at' in flag_copy and flag_copy['created_at']:
        flag_copy['created_at'] = flag_copy['created_at'].isoformat()
    if 'updated_at' in flag_copy and flag_copy['updated_at']:
        flag_copy['updated_at'] = flag_copy['updated_at'].isoformat()
    return orjson.dumps(flag_copy)

async def set_flag_in_cache(flag_id: str, flag_data: dict):
    await redis_client.set(f"flag:{flag_id}", serialize_flag(flag_data), ex=60)

async def delete_flag_from_cache(flag_id: str):
    deleted = await redis_client.delete(f"flag:{flag_id}")
