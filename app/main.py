from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine
from .models import user, subject, note, calendar_event
from .api import auth

# Criar tabelas
user.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="API para aplicação de estudos",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

@app.get("/")
async def root():
    return {"message": "StudyApp API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}