from fastapi import Header, HTTPException
from app import database
from app.middleware.rate_limit import check_rate_limit
import hashlib

async def get_api_key(x_api_key: str = Header(...)) -> dict:
    key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()
    
    async with database.pool.acquire() as connection:
        result = await connection.fetchrow(
            "SELECT * FROM api_keys WHERE key_hash = $1",
            key_hash
        )
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid API key")

    rate_limit_info = await check_rate_limit(result['key_id'], result['rate_limit'])
    
    async with database.pool.acquire() as connection:
        await connection.execute(
            "UPDATE api_keys SET last_used_at = NOW() WHERE key_id = $1",
            result['key_id']
        )
        
    api_key_dict = dict(result)
    api_key_dict['rate_limit_info'] = rate_limit_info  
    return api_key_dict