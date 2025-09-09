# app/schemas/calendar_event.py
from pydantic import BaseModel
from datetime import date, datetime, time
from typing import Optional

class EventTypeBase(BaseModel):
    name: str
    default_reminder_days: int = 1
    color: str = "#3B82F6"

class EventTypeResponse(EventTypeBase):
    id: int
    
    class Config:
        from_attributes = True

class CalendarEventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: date
    event_time: Optional[time] = None
    event_type_id: int
    subject_id: Optional[int] = None
    reminder_days: Optional[int] = None

class CalendarEventCreate(CalendarEventBase):
    pass

class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[date] = None
    event_time: Optional[time] = None
    event_type_id: Optional[int] = None
    subject_id: Optional[int] = None
    reminder_days: Optional[int] = None

class CalendarEventResponse(CalendarEventBase):
    id: int
    user_id: int
    reminder_sent: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Para resposta com detalhes incluindo tipo de evento e matéria
class CalendarEventWithDetails(CalendarEventResponse):
    event_type: EventTypeResponse
    subject: Optional["SubjectResponse"] = None
    
    class Config:
        from_attributes = True

# Import necessário para referência circular
from .subject import SubjectResponse
CalendarEventWithDetails.model_rebuild()