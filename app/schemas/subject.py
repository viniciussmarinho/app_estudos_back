# app/schemas/subject.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SubjectBase(BaseModel):
    name: str
    period: int
    color: str = "#3B82F6"

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    period: Optional[int] = None
    color: Optional[str] = None

class SubjectResponse(SubjectBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True