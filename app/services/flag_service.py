from app import database
from typing import Optional
from app.cache import get_flag_from_cache, set_flag_in_cache, delete_flag_from_cache
from app.services.snapshot import get_from_snapshot, update_snapshot, delete_from_snapshot
import logging

logger = logging.getLogger("feature_flags")

async def get_flag(flag_id: str) -> Optional[dict]:
    try:
        cached_flag = await get_flag_from_cache(flag_id)
        if cached_flag:
            update_snapshot(flag_id, cached_flag)
            return cached_flag
    except Exception as e:
        logger.error("Redis cache error", extra={'context': {'error': str(e), 'flag_id': flag_id}})
    
    try:
        async with database.pool.acquire() as connection:
            result = await connection.fetchrow(
                "SELECT * FROM flags WHERE flag_id = $1",
                flag_id
            )
    
        if result:
            result_dict = dict(result)
            update_snapshot(flag_id, result_dict)

            try:
                await set_flag_in_cache(flag_id, result_dict)
            except Exception:
                pass
                
            return result_dict
    except Exception as e:
        logger.error("Database query error", extra={'context': {'error': str(e), 'flag_id': flag_id}})

    snapshot_flag = get_from_snapshot(flag_id)
    if snapshot_flag:  
        logger.warning("Serving from snapshot (degraded mode)", extra={'context': {'flag_id': flag_id}})
        return snapshot_flag
    
    return None


async def list_flags(environment: Optional[str] = None) -> list[dict]:
    async with database.pool.acquire() as connection:
        if environment:
            result = await connection.fetch(
                "SELECT * FROM flags WHERE environment = $1", environment
            )
        else:
            result = await connection.fetch(
                "SELECT * FROM flags"
            )
        return result

async def create_flag(flag_data: dict) -> dict:
    async with database.pool.acquire() as connection:
        insert_query = """ INSERT INTO flags (flag_id, name, description, enabled, rollout_percentage, environment) 
                        VALUES ($1, $2, $3, $4, $5, $6) 
                        RETURNING * """
        row = await connection.fetchrow(insert_query,
            flag_data['flag_id'],
            flag_data['name'],
            flag_data.get('description'),
            flag_data['enabled'],
            flag_data['rollout_percentage'],
            flag_data['environment']
        )
        return row

async def update_flag(flag_id: str, updates: dict) -> Optional[dict]:
    async with database.pool.acquire() as connection:
        update_query = """UPDATE flags 
                        SET name = COALESCE($2, name), description = COALESCE($3, description), enabled = COALESCE($4, enabled), rollout_percentage = COALESCE($5, rollout_percentage), environment = COALESCE($6, environment), version = version + 1, updated_at = NOW()
                        WHERE flag_id = $1
                        RETURNING *"""
    
        row = await connection.fetchrow(
            update_query,
            flag_id,
            updates.get('name'),
            updates.get('description'),
            updates.get('enabled'),
            updates.get('rollout_percentage'),
            updates.get('environment')
        )
    
    if row:
        await delete_flag_from_cache(flag_id)
    return row
    

async def delete_flag(flag_id: str) -> bool:
    delete_query = "DELETE FROM flags WHERE flag_id = $1"
    async with database.pool.acquire() as connection:
        deleted = await connection.execute(delete_query, flag_id)
    
    if "1" in deleted:
        await delete_flag_from_cache(flag_id) 
        delete_from_snapshot(flag_id)
    return "1" in deleted 

