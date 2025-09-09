from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..models.subject import Subject
from ..schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse
from ..utils.dependencies import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[SubjectResponse])
async def get_subjects(
    period: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lista todas as matérias do usuário"""
    query = db.query(Subject).filter(Subject.user_id == current_user.id)
    if period:
        query = query.filter(Subject.period == period)
    
    subjects = query.order_by(Subject.period.asc(), Subject.name.asc()).all()
    return subjects

@router.post("/", response_model=SubjectResponse)
async def create_subject(
    subject_data: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cria nova matéria"""
    # Verifica se já existe matéria com mesmo nome no mesmo período
    existing_subject = db.query(Subject).filter(
        Subject.user_id == current_user.id,
        Subject.name == subject_data.name,
        Subject.period == subject_data.period
    ).first()
    
    if existing_subject:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subject already exists in this period"
        )
    
    db_subject = Subject(
        **subject_data.dict(),
        user_id=current_user.id
    )
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    
    return db_subject

@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Atualiza matéria"""
    db_subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    
    if not db_subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    update_data = subject_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_subject, field, value)
    
    db.commit()
    db.refresh(db_subject)
    
    return db_subject

@router.delete("/{subject_id}")
async def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Deleta matéria"""
    db_subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    
    if not db_subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    db.delete(db_subject)
    db.commit()
    
    return {"message": "Subject deleted successfully"}
