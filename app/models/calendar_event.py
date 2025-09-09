from sqlalchemy import Column, Integer, String, Text, Date, Time, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    event_date = Column(Date, nullable=False, index=True)
    event_time = Column(Time)
    event_type_id = Column(Integer, ForeignKey("event_types.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reminder_days = Column(Integer, default=1)
    reminder_sent = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    event_type = relationship("EventType", back_populates="calendar_events")
    subject = relationship("Subject", back_populates="calendar_events")
    user = relationship("User", back_populates="calendar_events")