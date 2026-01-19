from fastapi import APIRouter, HTTPException, Depends
from app.api.dependencies import get_api_key
from app.services import flag_service
from app.models import FlagCreate, FlagUpdate
from typing import Optional

router = APIRouter(prefix="/api/v1")

@router.get("/flags/{flag_id}")
async def get_flag(flag_id: str, api_key: dict = Depends(get_api_key)):
    flag = await flag_service.get_flag(flag_id)
    if not flag:
        raise HTTPException(status_code = 404, detail = "Flag not found")

    return flag

@router.get("/flags")
async def list_flags(environment: Optional[str] = None, api_key: dict = Depends(get_api_key)):
    flags = await flag_service.list_flags(environment)
    return {
        "flags": flags,
        "count": len(flags),
        "environment": environment
    }

@router.post("/flags", status_code = 201)
async def create_flag(flag: FlagCreate, api_key: dict = Depends(get_api_key)):
    flag_dict = flag.model_dump()
    created_flag = await flag_service.create_flag(flag_dict)
    return created_flag

@router.put("/flags/{flag_id}")
async def update_flag(flag_id: str, updates: FlagUpdate, api_key: dict = Depends(get_api_key)):
    updates_dict = updates.model_dump(exclude_unset = True)
    updated_flag = await flag_service.update_flag(flag_id, updates_dict)
    if not updated_flag:
        raise HTTPException(status_code = 404, detail = "Flag not found")
    
    return updated_flag

@router.delete("/flags/{flag_id}", status_code = 204)
async def delete_flag(flag_id: str, api_key: dict = Depends(get_api_key)):
    deleted = await flag_service.delete_flag(flag_id)
    if not deleted:
        raise HTTPException(status_code = 404, detail = "Flag not found")
    
    return

from app.services.evaluation import evaluate_flag_for_user
from app.models import FlagEvaluateResponse
from datetime import datetime

@router.get("/flags/{flag_id}/evaluate")
async def evaluate_flag(flag_id: str, user_id: str, environment: str = "prod", api_key: dict = Depends(get_api_key)):
    flag = await flag_service.get_flag(flag_id)
    if not flag:
        raise HTTPException(status_code = 404, detail = "Flag not found")
    if not flag['enabled']:
        return {
            "flag_id": flag_id,
            "enabled": False,
            "user_id": user_id,
            "evaluated_at": datetime.utcnow()
        }
    evaluation_bool = evaluate_flag_for_user(user_id, flag_id, flag['rollout_percentage'])
    return {
        "flag_id": flag_id,
        "enabled": evaluation_bool,
        "user_id": user_id,
        "evaluated_at": datetime.now()
    }

