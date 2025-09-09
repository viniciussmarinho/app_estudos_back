from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User, UserSettings
from ..models.password_reset import PasswordResetToken
from ..schemas.auth import UserRegister, UserLogin, Token, ForgotPassword, ResetPassword, UserResponse
from ..utils.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    generate_reset_token,
    create_reset_token_expires
)
from ..services.email_service import email_service
from ..config import settings
from datetime import datetime

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Registra novo usuário"""
    # Verifica se email já existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Cria novo usuário
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Cria configurações padrão do usuário
    user_settings = UserSettings(user_id=db_user.id)
    db.add(user_settings)
    db.commit()
    
    return db_user

@router.post("/login", response_model=Token)
async def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    """Faz login do usuário"""
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
async def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):
    """Solicita reset de senha"""
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        # Não revela se o email existe ou não por segurança
        return {"message": "If this email exists, you will receive a reset link"}
    
    # Gera token de reset
    reset_token = generate_reset_token()
    expires_at = create_reset_token_expires()
    
    # Salva token no banco
    db_token = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    
    # Envia email
    await email_service.send_password_reset_email(
        to_email=user.email,
        reset_token=reset_token,
        user_name=user.name
    )
    
    return {"message": "If this email exists, you will receive a reset link"}

@router.post("/reset-password")
async def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    """Redefine senha usando token"""
    # Busca token válido
    token_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == data.token,
        PasswordResetToken.used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()
    
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    # Busca usuário
    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Atualiza senha
    user.password_hash = get_password_hash(data.new_password)
    
    # Marca token como usado
    token_record.used = True
    
    db.commit()
    
    return {"message": "Password updated successfully"}