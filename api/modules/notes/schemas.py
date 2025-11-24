"""
Notes module schemas.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class NoteCategoryCreate(BaseModel):
    """Schema for creating a note category."""
    name: str = Field(..., min_length=1, max_length=100)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None


class NoteCategoryUpdate(BaseModel):
    """Schema for updating a note category."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None


class NoteCategoryResponse(BaseModel):
    """Schema for note category response."""
    id: UUID
    name: str
    color: Optional[str]
    icon: Optional[str]
    description: Optional[str]
    parent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NoteCreate(BaseModel):
    """Schema for creating a note."""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(default="")
    content_type: str = Field(default="html")
    category_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    is_pinned: bool = False
    
    @validator("tags")
    def validate_tags(cls, v):
        if v is not None:
            # Remove duplicates and empty strings
            return list(set(filter(None, v)))
        return v


class NoteUpdate(BaseModel):
    """Schema for updating a note."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    content_type: Optional[str] = None
    category_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None
    is_favorite: Optional[bool] = None
    
    @validator("tags")
    def validate_tags(cls, v):
        if v is not None:
            return list(set(filter(None, v)))
        return v


class NoteResponse(BaseModel):
    """Schema for note response."""
    id: UUID
    title: str
    content: str
    content_type: str
    category_id: Optional[UUID]
    category: Optional[NoteCategoryResponse]
    tags: Optional[List[str]]
    is_pinned: bool
    is_archived: bool
    is_favorite: bool
    is_shared: bool
    share_token: Optional[str]
    word_count: int
    character_count: int
    reading_time_minutes: int
    created_at: datetime
    updated_at: datetime
    last_viewed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    """Schema for note list item (without full content)."""
    id: UUID
    title: str
    content_preview: str  # First 150 characters
    category_id: Optional[UUID]
    category: Optional[NoteCategoryResponse]
    tags: Optional[List[str]]
    is_pinned: bool
    is_archived: bool
    is_favorite: bool
    word_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NoteVersionResponse(BaseModel):
    """Schema for note version response."""
    id: UUID
    note_id: UUID
    title: str
    content: str
    version_number: int
    created_at: datetime
    created_by: Optional[UUID]
    
    class Config:
        from_attributes = True


class PaginatedNotesResponse(BaseModel):
    """Schema for paginated notes response."""
    items: List[NoteListResponse]
    total: int
    page: int
    size: int
    pages: int
