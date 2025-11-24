# Module Development Guide

This guide explains how to create new modules for Lexicon.

## Module Structure

Every module follows this structure:

```
api/modules/your_module/
├── __init__.py
├── module_config.py    # Module metadata and configuration
├── models.py           # Database models
├── schemas.py          # Pydantic schemas
├── routes.py           # API endpoints
├── crud.py             # Database operations (optional)
├── service.py          # Business logic (optional)
├── permissions.py      # Custom permissions (optional)
├── tasks.py            # Background tasks (optional)
└── tests/              # Unit tests
    ├── __init__.py
    ├── test_routes.py
    └── test_models.py
```

## Step 1: Create Module Directory

```bash
mkdir -p api/modules/your_module
touch api/modules/your_module/__init__.py
```

## Step 2: Define Module Configuration

Create `module_config.py`:

```python
module_config = {
    "name": "YourModule",
    "slug": "your-module",
    "version": "1.0.0",
    "description": "Description of your module",
    "author": "Your Name",
    "icon": "IconName",  # Icon from your icon library
    "color": "#3B82F6",
    
    # API configuration
    "api_router": "routes.py",
    
    # Permissions
    "permissions": [
        {
            "name": "your_module.view",
            "display_name": "View Your Module",
            "description": "View your module data",
            "resource": "your_module",
            "action": "view",
        },
        {
            "name": "your_module.create",
            "display_name": "Create in Your Module",
            "description": "Create new items",
            "resource": "your_module",
            "action": "create",
        },
        # Add more permissions as needed
    ],
    
    # Frontend widgets (optional)
    "widgets": [
        {
            "name": "YourModuleWidget",
            "description": "Widget description",
            "sizes": ["small", "medium", "large"],
        },
    ],
    
    # Event signals (optional)
    "signals": [
        "your_module.item_created",
        "your_module.item_updated",
    ],
    
    # Dependencies (optional)
    "dependencies": [],
    
    # Settings schema (optional)
    "settings_schema": {
        "setting_key": {
            "type": "string",
            "default": "default_value",
        },
    },
}
```

## Step 3: Create Database Models

Create `models.py`:

```python
from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from api.database import Base

class YourModel(Base):
    __tablename__ = "your_module_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Your fields
    name = Column(String(255), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<YourModel {self.name}>"
```

## Step 4: Create Pydantic Schemas

Create `schemas.py`:

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, UUID4, ConfigDict

class YourModelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

class YourModelCreate(YourModelBase):
    pass

class YourModelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)

class YourModelResponse(YourModelBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

## Step 5: Create API Routes

Create `routes.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from api.database import get_db
from api.core import models as core_models
from api.core.dependencies import get_current_active_user, require_permissions
from api.modules.your_module import models, schemas

router = APIRouter()

@router.get("/", response_model=list[schemas.YourModelResponse])
async def list_items(
    current_user: core_models.User = Depends(require_permissions("your_module.view")),
    db: Session = Depends(get_db)
):
    """List all items for current user."""
    items = db.query(models.YourModel).filter(
        models.YourModel.user_id == current_user.id
    ).all()
    return items

@router.post("/", response_model=schemas.YourModelResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_create: schemas.YourModelCreate,
    current_user: core_models.User = Depends(require_permissions("your_module.create")),
    db: Session = Depends(get_db)
):
    """Create a new item."""
    item = models.YourModel(
        user_id=current_user.id,
        **item_create.model_dump()
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

# Add more routes as needed (GET by ID, PUT, DELETE, etc.)
```

## Step 6: Auto-Registration

That's it! The module will be automatically discovered and registered when the API starts.

The module loader will:
1. Scan `api/modules/` for directories
2. Look for `module_config.py` in each directory
3. Load the configuration
4. Register the API router at `/{slug}/`
5. Create permissions in the database

## Step 7: Testing

Create tests in `tests/test_routes.py`:

```python
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_list_items():
    # Your test here
    pass
```

Run tests:

```bash
pytest api/modules/your_module/tests/
```

## Best Practices

### 1. Use Permission Checks

Always use `require_permissions()` dependency:

```python
@router.get("/")
async def list_items(
    current_user: User = Depends(require_permissions("your_module.view")),
    db: Session = Depends(get_db)
):
    ...
```

### 2. Filter by User

Always filter data by `user_id` to ensure data isolation:

```python
items = db.query(models.YourModel).filter(
    models.YourModel.user_id == current_user.id
).all()
```

### 3. Use UUIDs

Always use UUIDs for primary keys:

```python
id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
```

### 4. Add Timestamps

Include `created_at` and `updated_at` in all models:

```python
created_at = Column(DateTime, default=datetime.utcnow)
updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 5. Validate Input

Use Pydantic for validation:

```python
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
```

### 6. Handle Errors

Return appropriate HTTP status codes:

```python
if not item:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Item not found"
    )
```

### 7. Document Endpoints

Add docstrings to all routes:

```python
@router.get("/")
async def list_items(...):
    """
    List all items for the current user.
    
    Returns a list of items with pagination support.
    """
    ...
```

## Example: Complete Module

See `api/modules/tasks/` for a complete working example.

## Frontend Integration

For frontend module development, see `web/docs/MODULE_DEVELOPMENT.md` (coming soon).

## Need Help?

- Check existing modules in `api/modules/`
- Read the core documentation in `docs/`
- Ask in GitHub Discussions
