"""
Configuration management for Lexicon API.
Loads settings from environment variables with sensible defaults.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Lexicon API"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "The core API for the Lexicon Personal Operating System"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Database
    DATABASE_URL: str = "postgresql://lexicon:lexicon@localhost:5432/lexicon_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour default
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password hashing
    PASSWORD_HASH_SCHEME: str = "argon2"  # argon2, bcrypt
    
    # MFA
    MFA_ISSUER_NAME: str = "Lexicon"
    MFA_BACKUP_CODES_COUNT: int = 10
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # File Storage (MinIO/S3)
    STORAGE_TYPE: str = "minio"  # minio, s3, local
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = "lexicon-files"
    
    # S3 (if using AWS S3)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_BUCKET_NAME: str = "lexicon-files"
    
    # Vector Database
    VECTOR_DB_TYPE: str = "pgvector"  # pgvector, chroma, qdrant
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    
    # AI Services
    AI_PROVIDER: str = "openai"  # openai, anthropic, local
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    LOCAL_LLM_ENDPOINT: Optional[str] = None
    
    # Email (for notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@lexicon.local"
    
    # Worker/Queue
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Audit Logging
    AUDIT_LOG_ENABLED: bool = True
    AUDIT_LOG_RETENTION_DAYS: int = 90
    
    # Module System
    MODULES_AUTO_DISCOVER: bool = True
    MODULES_DIR: str = "api/modules"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience export
settings = get_settings()
