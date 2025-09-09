# backend/app/models/password_reset.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    # A linha abaixo corrige o erro original, conectando esta tabela à tabela "users"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relação de volta para o User
    user = relationship("User", back_populates="password_reset_tokens")