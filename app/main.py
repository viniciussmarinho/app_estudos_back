# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base
from .models import user, subject, note, calendar_event, password_reset
from .api import auth, subjects, notes, calendar, users, flashcards

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="API para aplicação de estudos",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(subjects.router, prefix="/api/subjects", tags=["Subjects"])
app.include_router(notes.router, prefix="/api/notes", tags=["Notes"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["Calendar"])
app.include_router(flashcards.router, prefix="/api/flashcards", tags=["Flashcards"])

@app.get("/")
async def root():
    return {"message": "StudyApp API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}