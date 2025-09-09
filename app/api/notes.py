from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models.user import User
from ..models.note import Note
from ..models.subject import Subject
from ..schemas.note import NoteCreate, NoteUpdate, NoteResponse, NoteWithSubject
from ..utils.dependencies import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[NoteWithSubject])
async def get_notes(
    subject_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lista todas as anotações do usuário"""
    query = db.query(Note).options(joinedload(Note.subject)).filter(
        Note.user_id == current_user.id
    )
    
    if subject_id:
        query = query.filter(Note.subject_id == subject_id)
    
    notes = query.order_by(Note.updated_at.desc()).all()
    return notes

@router.get("/{note_id}", response_model=NoteWithSubject)
async def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém uma anotação específica"""
    note = db.query(Note).options(joinedload(Note.subject)).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    return note

@router.post("/", response_model=NoteResponse)
async def create_note(
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cria nova anotação"""
    # Verifica se a matéria existe e pertence ao usuário
    subject = db.query(Subject).filter(
        Subject.id == note_data.subject_id,
        Subject.user_id == current_user.id
    ).first()
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    db_note = Note(
        **note_data.dict(),
        user_id=current_user.id
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    return db_note

@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Atualiza anotação"""
    db_note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()
    
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    update_data = note_data.dict(exclude_unset=True)
    
    # Se está mudando de matéria, verifica se a nova matéria existe
    if 'subject_id' in update_data:
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
        setattr(db_note, field, value)
    
    db.commit()
    db.refresh(db_note)
    
    return db_note

@router.delete("/{note_id}")
async def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Deleta anotação"""
    db_note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()
    
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    db.delete(db_note)
    db.commit()
    
    return {"message": "Note deleted successfully"}
