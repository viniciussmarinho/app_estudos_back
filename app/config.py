from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "mssql+pyodbc://username:password@server/StudyAppDB?driver=ODBC+Driver+17+for+SQL+Server"
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = "StudyApp"
    
    # Frontend
    frontend_url: str = "http://localhost:3000"
    
    # App
    app_name: str = "StudyApp API"
    debug: bool = True
    
    # Password Reset
    password_reset_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()