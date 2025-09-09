from typing import List
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models.user import User, EventType
from ..models.calendar_event import CalendarEvent
from ..models.subject import Subject
from ..schemas.calendar_event import (
    CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse, 
    CalendarEventWithDetails, EventTypeResponse
)
from ..utils.dependencies import get_current_active_user

router = APIRouter()

@router.get("/event-types/", response_model=List[EventTypeResponse])
async def get_event_types(db: Session = Depends(get_db)):
    """Lista todos os tipos de eventos"""
    event_types = db.query(EventType).all()
    return event_types

@router.get("/", response_model=List[CalendarEventWithDetails])
async def get_calendar_events(
    start_date: date = None,
    end_date: date = None,
    event_type_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lista eventos do calendário"""
    query = db.query(CalendarEvent).options(
        joinedload(CalendarEvent.event_type),
        joinedload(CalendarEvent.subject)
    ).filter(CalendarEvent.user_id == current_user.id)
    
    if start_date:
        query = query.filter(CalendarEvent.event_date >= start_date)
    if end_date:
        query = query.filter(CalendarEvent.event_date <= end_date)
    if event_type_id:
        query = query.filter(CalendarEvent.event_type_id == event_type_id)
    
    events = query.order_by(CalendarEvent.event_date.asc()).all()
    return events

@router.get("/{event_id}", response_model=CalendarEventWithDetails)
async def get_calendar_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém um evento específico"""
    event = db.query(CalendarEvent).options(
        joinedload(CalendarEvent.event_type),
        joinedload(CalendarEvent.subject)
    ).filter(
        CalendarEvent.id == event_id,
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return event

@router.post("/", response_model=CalendarEventResponse)
async def create_calendar_event(
    event_data: CalendarEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cria novo evento no calendário"""
    # Verifica se o tipo de evento existe
    event_type = db.query(EventType).filter(
        EventType.id == event_data.event_type_id
    ).first()
    
    if not event_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event type not found"
        )
    
    # Se há matéria associada, verifica se pertence ao usuário
    if event_data.subject_id:
        subject = db.query(Subject).filter(
            Subject.id == event_data.subject_id,
            Subject.user_id == current_user.id
        ).first()
        
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
    
    # Se reminder_days não foi especificado, usa o padrão do tipo de evento
    reminder_days = event_data.reminder_days
    if reminder_days is None:
        reminder_days = event_type.default_reminder_days
    
    db_event = CalendarEvent(
        title=event_data.title,
        description=event_data.description,
        event_date=event_data.event_date,
        event_time=event_data.event_time,
        event_type_id=event_data.event_type_id,
        subject_id=event_data.subject_id,
        reminder_days=reminder_days,
        user_id=current_user.id
    )
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    return db_event

@router.put("/{event_id}", response_model=CalendarEventResponse)
async def update_calendar_event(
    event_id: int,
    event_data: CalendarEventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Atualiza evento do calendário"""
    db_event = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_id,
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    update_data = event_data.dict(exclude_unset=True)
    
    # Validações similares ao create
    if 'event_type_id' in update_data:
        event_type = db.query(EventType).filter(
            EventType.id == update_data['event_type_id']
        ).first()
        if not event_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event type not found"
            )
    
    if 'subject_id' in update_data and update_data['subject_id']:
        subject = db.query(Subject).filter(
            Subject.id == update_data['subject_id'],
            Subject.user_id == current_user.id
        ).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
    
    for field, value in update_data.items():
        setattr(db_event, field, value)
    
    db.commit()
    db.refresh(db_event)
    
    return db_event

@router.delete("/{event_id}")
async def delete_calendar_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Deleta evento do calendário"""
    db_event = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_id,
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    db.delete(db_event)
    db.commit()
    
    return {"message": "Event deleted successfully"}