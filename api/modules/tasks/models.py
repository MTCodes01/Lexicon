"""
Database models for Tasks module.
"""
from datetime import datetime
from typing import Optional
import uuid
import enum

from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey, Enum as SQLEnum, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from api.database import Base


class TaskPriority(str, enum.Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, enum.Enum):
    """Task status."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Task(Base):
    """Task model."""
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Task information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Status and priority
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.TODO, nullable=False, index=True)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False, index=True)
    
    # Dates
    due_date = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Organization
    tags = Column(JSON, nullable=True)  # Store as JSON array for SQLite compatibility
    
    # Notification tracking
    notification_24h_sent = Column(Boolean, default=False, nullable=False)
    notification_1h_sent = Column(Boolean, default=False, nullable=False)
    notification_overdue_sent = Column(Boolean, default=False, nullable=False)
    last_notification_at = Column(DateTime, nullable=True)
    
    # Sharing
    is_shared = Column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    
    __table_args__ = (
        Index('ix_tasks_user_status', 'user_id', 'status'),
        Index('ix_tasks_user_priority', 'user_id', 'priority'),
    )
    
    def __repr__(self):
        return f"<Task {self.title}>"
