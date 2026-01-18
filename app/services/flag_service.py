from app import database
from typing import Optional

async def get_flag(flag_id: str) -> Optional[dict]:
    async with database.pool.acquire() as connection:
        result = await connection.fetchrow(
            "SELECT * FROM flags WHERE flag_id = $1",
            flag_id
        )
        return result

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
                        SET name = $2, description = $3, enabled = $4, rollout_percentage = $5, environment = $6, version = version + 1, updated_at = NOW()
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

    return row
    

async def delete_flag(flag_id: str) -> bool:
    delete_query = "DELETE FROM flags WHERE flag_id = $1"
    async with database.pool.acquire() as connection:
        deleted = await connection.execute(delete_query, flag_id)

    return "1" in deleted 

