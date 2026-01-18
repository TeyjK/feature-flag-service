from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class Flag(BaseModel):
    flag_id: str
    name: str
    description: Optional[str]
    enabled: bool
    rollout_percentage: int
    environment: str
    created_at: datetime
    updated_at: datetime
    version: int

class FlagCreate(BaseModel):
    flag_id: str 
    name: str 
    description: Optional[str] = None
    enabled: bool = False
    rollout_percentage: int = 0
    environment: str

class FlagUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None 
    enabled: Optional[bool] = None
    rollout_percentage: Optional[int] = None 
    environment: Optional[str] = None

class FlagEvaluateResponse(BaseModel):
    flag_id: str
    enabled: bool
    user_id: str
    evaluated_at: datetime