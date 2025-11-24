"""
Notes module CRUD operations.
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from typing import List, Optional
from uuid import UUID
import re

from api.modules.notes.models import Note, NoteCategory, NoteVersion
from api.modules.notes.schemas import NoteCreate, NoteUpdate, NoteCategoryCreate, NoteCategoryUpdate


def calculate_metadata(content: str) -> dict:
    """Calculate word count, character count, and reading time."""
    # Remove HTML tags for accurate word count
    text = re.sub(r'<[^>]+>', '', content)
    
    words = len(text.split())
    characters = len(text)
    reading_time = max(1, words // 200)  # Average reading speed: 200 words/minute
    
    return {
        "word_count": words,
        "character_count": characters,
        "reading_time_minutes": reading_time,
    }


# Note CRUD
def create_note(db: Session, note: NoteCreate, user_id: UUID) -> Note:
    """Create a new note."""
    metadata = calculate_metadata(note.content)
    
    db_note = Note(
        user_id=user_id,
        title=note.title,
        content=note.content,
        content_type=note.content_type,
        category_id=note.category_id,
        tags=note.tags,
        is_pinned=note.is_pinned,
        **metadata,
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def get_note(db: Session, note_id: UUID, user_id: UUID) -> Optional[Note]:
    """Get a note by ID."""
    return db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == user_id
    ).options(joinedload(Note.category)).first()


def get_notes(
    db: Session,
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category_id: Optional[UUID] = None,
    tag: Optional[str] = None,
    is_pinned: Optional[bool] = None,
    is_archived: Optional[bool] = None,
    is_favorite: Optional[bool] = None,
) -> tuple[List[Note], int]:
    """Get notes with filters and pagination."""
    query = db.query(Note).filter(Note.user_id == user_id)
    
    # Apply filters
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Note.title.ilike(search_pattern),
                Note.content.ilike(search_pattern)
            )
        )
    
    if category_id:
        query = query.filter(Note.category_id == category_id)
    
    if tag:
        # Search in JSON array
        query = query.filter(Note.tags.contains([tag]))
    
    if is_pinned is not None:
        query = query.filter(Note.is_pinned == is_pinned)
    
    if is_archived is not None:
        query = query.filter(Note.is_archived == is_archived)
    
    if is_favorite is not None:
        query = query.filter(Note.is_favorite == is_favorite)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and sorting
    notes = query.options(joinedload(Note.category)).order_by(
        Note.is_pinned.desc(),
        Note.updated_at.desc()
    ).offset(skip).limit(limit).all()
    
    return notes, total


def update_note(db: Session, note_id: UUID, note_update: NoteUpdate, user_id: UUID) -> Optional[Note]:
    """Update a note."""
    db_note = get_note(db, note_id, user_id)
    if not db_note:
        return None
    
    update_data = note_update.dict(exclude_unset=True)
    
    # Recalculate metadata if content changed
    if "content" in update_data:
        metadata = calculate_metadata(update_data["content"])
        update_data.update(metadata)
    
    for field, value in update_data.items():
        setattr(db_note, field, value)
    
    db.commit()
    db.refresh(db_note)
    return db_note


def delete_note(db: Session, note_id: UUID, user_id: UUID) -> bool:
    """Delete a note."""
    db_note = get_note(db, note_id, user_id)
    if not db_note:
        return False
    
    db.delete(db_note)
    db.commit()
    return True


def get_all_tags(db: Session, user_id: UUID) -> List[str]:
    """Get all unique tags for a user."""
    notes = db.query(Note.tags).filter(
        Note.user_id == user_id,
        Note.tags.isnot(None)
    ).all()
    
    # Flatten and deduplicate tags
    all_tags = set()
    for note in notes:
        if note.tags:
            all_tags.update(note.tags)
    
    return sorted(list(all_tags))


# Category CRUD
def create_category(db: Session, category: NoteCategoryCreate, user_id: UUID) -> NoteCategory:
    """Create a new category."""
    db_category = NoteCategory(
        user_id=user_id,
        **category.dict()
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_category(db: Session, category_id: UUID, user_id: UUID) -> Optional[NoteCategory]:
    """Get a category by ID."""
    return db.query(NoteCategory).filter(
        NoteCategory.id == category_id,
        NoteCategory.user_id == user_id
    ).first()


def get_categories(db: Session, user_id: UUID) -> List[NoteCategory]:
    """Get all categories for a user."""
    return db.query(NoteCategory).filter(
        NoteCategory.user_id == user_id
    ).order_by(NoteCategory.name).all()


def update_category(db: Session, category_id: UUID, category_update: NoteCategoryUpdate, user_id: UUID) -> Optional[NoteCategory]:
    """Update a category."""
    db_category = get_category(db, category_id, user_id)
    if not db_category:
        return None
    
    update_data = category_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: UUID, user_id: UUID) -> bool:
    """Delete a category."""
    db_category = get_category(db, category_id, user_id)
    if not db_category:
        return False
    
    db.delete(db_category)
    db.commit()
    return True
