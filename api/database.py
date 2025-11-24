"""
Database configuration and session management for Lexicon.
Supports both sync and async database operations.
"""
from typing import Generator
from sqlalchemy import create_engine, event, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from api.config import settings

# Naming convention for constraints (helps with migrations)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

# Create engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base(metadata=metadata)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database sessions.
    Automatically handles session lifecycle.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.
    Should be called on application startup.
    """
    # Import all models here to ensure they're registered with Base
    from api.core.models import (
        User, Role, Permission, UserRole, 
        AuditLog, Setting, APIKey, Session as SessionModel,
        MFADevice
    )
    
    Base.metadata.create_all(bind=engine)


def close_db() -> None:
    """
    Close database connections.
    Should be called on application shutdown.
    """
    engine.dispose()


# Event listeners for connection management
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set SQLite pragmas if using SQLite (for testing)."""
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()