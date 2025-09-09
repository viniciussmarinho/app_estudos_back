# app/schemas/note.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .subject import SubjectResponse

class NoteBase(BaseModel):
    title: str
    content: str
    subject_id: int

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    subject_id: Optional[int] = None

class NoteResponse(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class NoteWithSubject(NoteResponse):
    subject: SubjectResponse
    
    class Config:
        from_attributes = True