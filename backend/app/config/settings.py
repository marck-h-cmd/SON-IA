"""
Configuración centralizada usando Pydantic Settings
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación SON-IA"""
    
    # Application
    APP_NAME: str = "SON-IA"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Database - PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "sonia_db"
    POSTGRES_USER: str = "sonia_user"
    POSTGRES_PASSWORD: str = "sonia_password"
    
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # Database - SQL Server (Legacy)
    MSSQL_HOST: str = "localhost"
    MSSQL_PORT: int = 1433
    MSSQL_DB: str = "integratel_bss"
    MSSQL_USER: str = "sa"
    MSSQL_PASSWORD: str = "password"
    
    @property
    def MSSQL_URL(self) -> str:
        return (
            f"mssql+pymssql://{self.MSSQL_USER}:{self.MSSQL_PASSWORD}"
            f"@{self.MSSQL_HOST}:{self.MSSQL_PORT}/{self.MSSQL_DB}"
        )
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
    
    # Main LLM API (Groq)
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.groq.com/openai/v1"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    
    # Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL_PRO: str = "gemini-1.5-pro"
    GEMINI_MODEL_FLASH: str = "gemini-1.5-flash"
    
    # Pinecone
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "us-west1-gcp"
    PINECONE_INDEX: str = "sonia-embeddings"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # OpenWA (Development)
    OPENWA_WEBHOOK_URL: str = "http://localhost:5000/teapi/whatsapp/webhook"

    # Open Gateway (Movistar / Telefónica)
    OPEN_GATEWAY_CLIENT_ID: str = ""
    OPEN_GATEWAY_CLIENT_SECRET: str = ""
    OPEN_GATEWAY_TOKEN_URL: str = "https://sandbox.opengateway.telefonica.com/apigateway/token"
    OPEN_GATEWAY_BASE_URL: str = "https://sandbox.opengateway.telefonica.com"

    # OpenWA (Gateway WhatsApp)
    OPENWA_API_KEY: str = ""
    OPENWA_BASE_URL: str = "http://localhost:2785"
    OPENWA_SESSION_NAME: str = "mi-session"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


# Singleton
_settings: Settings | None = None


def get_settings() -> Settings:
    """Retorna la instancia única de Settings"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings