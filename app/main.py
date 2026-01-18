from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import init_db, close_db
from app.cache import init_redis, close_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_redis()

    yield

    await close_db()
    await close_redis()

app = FastAPI(lifespan=lifespan)

from app.api import flags
app.include_router(flags.router)

@app.get("/health")
async def health_check():
    from app import database, cache
    
    db_status = "connected" if database.pool else "disconnected"
    redis_status = "connected" if cache.redis_client else "disconnected"
    
    return {
        "status": "healthy",
        "database": db_status,
        "cache": redis_status
    }