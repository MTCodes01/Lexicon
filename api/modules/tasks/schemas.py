"""
Pydantic schemas for Tasks module.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, UUID4, ConfigDict
from enum import Enum


class TaskPriorityEnum(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatusEnum(str, Enum):
    """Task status."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskBase(BaseModel):
    """Base task schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatusEnum] = None
    priority: Optional[TaskPriorityEnum] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None


class TaskResponse(TaskBase):
    """Schema for task response."""
    id: UUID4
    user_id: UUID4
    status: TaskStatusEnum
    is_shared: bool
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """Schema for paginated task list response."""
    items: List[TaskResponse]
    total: int
    page: int
    page_size: int
