from fastapi import APIRouter, HTTPException
from app.services import flag_service
from app.models import FlagCreate, FlagUpdate
from typing import Optional

router = APIRouter(prefix="/api/v1")

@router.get("/flags/{flag_id}")
async def get_flag(flag_id: str):
    flag = await flag_service.get_flag(flag_id)
    if not flag:
        raise HTTPException(status_code = 404, detail = "Flag not found")

    return flag

@router.get("/flags")
async def list_flags(environment: Optional[str] = None):
    flags = await flag_service.list_flags(environment)
    return {
        "flags": flags,
        "count": len(flags),
        "environment": environment
    }

@router.post("/flags", status_code = 201)
async def create_flag(flag: FlagCreate):
    flag_dict = flag.model_dump()
    created_flag = await flag_service.create_flag(flag_dict)
    return created_flag

@router.put("/flags/{flag_id}")
async def update_flag(flag_id: str, updates: FlagUpdate):
    updates_dict = updates.model_dump(exclude_unset = True)
    updated_flag = await flag_service.update_flag(flag_id, updates_dict)
    if not updated_flag:
        raise HTTPException(status_code = 404, detail = "Flag not found")
    
    return updated_flag

@router.delete("/flags/{flag_id}", status_code = 204)
async def delete_flag(flag_id: str):
    deleted = await flag_service.delete_flag(flag_id)
    if not deleted:
        raise HTTPException(status_code = 404, detail = "Flag not found")
    
    return