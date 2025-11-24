"""
Notes module models.
"""
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from api.database import Base


class ContentType(str, enum.Enum):
    """Content type for notes."""
    MARKDOWN = "markdown"
    HTML = "html"
    PLAIN = "plain"


class NoteCategory(Base):
    """Note category model."""
    __tablename__ = "note_categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Category details
    name = Column(String(100), nullable=False)
    color = Column(String(7), nullable=True)  # Hex color like #FF5733
    icon = Column(String(50), nullable=True)  # Emoji or icon name
    description = Column(Text, nullable=True)
    
    # Nested categories
    parent_id = Column(UUID(as_uuid=True), ForeignKey("note_categories.id", ondelete="CASCADE"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="note_categories")
    notes = relationship("Note", back_populates="category", cascade="all, delete-orphan")
    children = relationship("NoteCategory", backref="parent", remote_side=[id])


class Note(Base):
    """Note model."""
    __tablename__ = "notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Content
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False, default="")
    content_type = Column(SQLEnum(ContentType), default=ContentType.HTML, nullable=False)
    
    # Organization
    category_id = Column(UUID(as_uuid=True), ForeignKey("note_categories.id", ondelete="SET NULL"), nullable=True, index=True)
    tags = Column(JSON, nullable=True)  # Array of strings
    
    # Status
    is_pinned = Column(Boolean, default=False, nullable=False, index=True)
    is_archived = Column(Boolean, default=False, nullable=False, index=True)
    is_favorite = Column(Boolean, default=False, nullable=False, index=True)
    
    # Sharing
    is_shared = Column(Boolean, default=False, nullable=False)
    share_token = Column(String(64), nullable=True, unique=True, index=True)
    
    # Metadata
    word_count = Column(Integer, default=0, nullable=False)
    character_count = Column(Integer, default=0, nullable=False)
    reading_time_minutes = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, index=True)
    last_viewed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notes")
    category = relationship("NoteCategory", back_populates="notes")
    versions = relationship("NoteVersion", back_populates="note", cascade="all, delete-orphan")


class NoteVersion(Base):
    """Note version history model."""
    __tablename__ = "note_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Version content
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    version_number = Column(Integer, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    note = relationship("Note", back_populates="versions")
    creator = relationship("User")
