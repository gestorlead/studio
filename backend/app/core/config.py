"""
FastAPI Application Configuration
Task: 1.8 - Integrate ORM Models with FastAPI
"""

import os
from typing import Optional, List
from pydantic import BaseSettings, validator
from functools import lru_cache


class Settings(BaseSettings):
    """Configurações da aplicação GestorLead Studio"""
    
    # Application
    APP_NAME: str = "GestorLead Studio API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-powered marketing automation platform"
    DEBUG: bool = False
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: Optional[str] = None
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "gestorlead"
    DATABASE_PASSWORD: str = "gestorlead_password"
    DATABASE_NAME: str = "gestorlead_studio"
    
    # Database Pool Settings
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('DATABASE_USER')}:{values.get('DATABASE_PASSWORD')}@{values.get('DATABASE_HOST')}:{values.get('DATABASE_PORT')}/{values.get('DATABASE_NAME')}"
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings"""
    return Settings()


# Create settings instance
settings = get_settings() 