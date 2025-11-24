"""
API routes for Tasks module.
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from api.database import get_db
from api.core import models as core_models
from api.core.dependencies import get_current_active_user, require_permissions
from api.modules.tasks import models, schemas


router = APIRouter()


@router.get("/", response_model=schemas.TaskListResponse)
async def list_tasks(
    status: Optional[schemas.TaskStatusEnum] = None,
    priority: Optional[schemas.TaskPriorityEnum] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: core_models.User = Depends(require_permissions("tasks.view")),
    db: Session = Depends(get_db)
):
    """
    List tasks for the current user.
    
    - **status**: Filter by status (optional)
    - **priority**: Filter by priority (optional)
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    """
    query = db.query(models.Task).filter(models.Task.user_id == current_user.id)
    
    # Apply filters
    if status:
        query = query.filter(models.Task.status == status)
    if priority:
        query = query.filter(models.Task.priority == priority)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    skip = (page - 1) * page_size
    tasks = query.order_by(models.Task.created_at.desc()).offset(skip).limit(page_size).all()
    
    return schemas.TaskListResponse(
        items=tasks,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_create: schemas.TaskCreate,
    current_user: core_models.User = Depends(require_permissions("tasks.create")),
    db: Session = Depends(get_db)
):
    """
    Create a new task.
    
    - **title**: Task title (required)
    - **description**: Task description (optional)
    - **priority**: Task priority (default: medium)
    - **due_date**: Due date (optional)
    - **tags**: List of tags (optional)
    """
    task = models.Task(
        user_id=current_user.id,
        **task_create.model_dump()
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return task


@router.get("/{task_id}", response_model=schemas.TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: core_models.User = Depends(require_permissions("tasks.view")),
    db: Session = Depends(get_db)
):
    """Get a specific task by ID."""
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task


@router.put("/{task_id}", response_model=schemas.TaskResponse)
async def update_task(
    task_id: UUID,
    task_update: schemas.TaskUpdate,
    current_user: core_models.User = Depends(require_permissions("tasks.edit")),
    db: Session = Depends(get_db)
):
    """Update a task."""
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update fields
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    # If status changed to completed, set completed_at
    if task_update.status == schemas.TaskStatusEnum.COMPLETED and not task.completed_at:
        task.completed_at = datetime.utcnow()
    elif task_update.status and task_update.status != schemas.TaskStatusEnum.COMPLETED:
        task.completed_at = None
    
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: core_models.User = Depends(require_permissions("tasks.delete")),
    db: Session = Depends(get_db)
):
    """Delete a task."""
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    db.delete(task)
    db.commit()
    
    return None


@router.post("/{task_id}/complete", response_model=schemas.TaskResponse)
async def complete_task(
    task_id: UUID,
    current_user: core_models.User = Depends(require_permissions("tasks.edit")),
    db: Session = Depends(get_db)
):
    """Mark a task as completed."""
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task.status = models.TaskStatus.COMPLETED
    task.completed_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(task)
    
    return task
