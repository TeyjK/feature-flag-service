import asyncio
import asyncpg

from app.config import settings

pool = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=settings.postgres_pool_min,
        max_size=settings.postgres_pool_max
    )
    print(f"Pool assigned: {pool}")

async def close_db():
    global pool
    await pool.close()
