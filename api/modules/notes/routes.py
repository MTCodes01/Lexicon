"""
Notes module API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from api.database import get_db
from api.core.dependencies import get_current_user, require_permissions
from api.core.models import User
from api.modules.notes import crud, schemas
from api.modules.notes.models import Note, NoteCategory

router = APIRouter(prefix="/notes", tags=["notes"])


# Category endpoints
@router.post("/categories", response_model=schemas.NoteCategoryResponse, status_code=201)
def create_category(
    category: schemas.NoteCategoryCreate,
    current_user: User = Depends(require_permissions("notes.create")),
    db: Session = Depends(get_db),
):
    """Create a new category."""
    return crud.create_category(db, category, current_user.id)


@router.get("/categories", response_model=List[schemas.NoteCategoryResponse])
def list_categories(
    current_user: User = Depends(require_permissions("notes.view")),
    db: Session = Depends(get_db),
):
    """List all categories."""
    return crud.get_categories(db, current_user.id)


@router.get("/categories/{category_id}", response_model=schemas.NoteCategoryResponse)
def get_category(
    category_id: UUID,
    current_user: User = Depends(require_permissions("notes.view")),
    db: Session = Depends(get_db),
):
    """Get a specific category."""
    category = crud.get_category(db, category_id, current_user.id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/categories/{category_id}", response_model=schemas.NoteCategoryResponse)
def update_category(
    category_id: UUID,
    category_update: schemas.NoteCategoryUpdate,
    current_user: User = Depends(require_permissions("notes.edit")),
    db: Session = Depends(get_db),
):
    """Update a category."""
    category = crud.update_category(db, category_id, category_update, current_user.id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/categories/{category_id}", status_code=204)
def delete_category(
    category_id: UUID,
    current_user: User = Depends(require_permissions("notes.delete")),
    db: Session = Depends(get_db),
):
    """Delete a category."""
    success = crud.delete_category(db, category_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return None


# Note endpoints
@router.post("/", response_model=schemas.NoteResponse, status_code=201)
def create_note(
    note: schemas.NoteCreate,
    current_user: User = Depends(require_permissions("notes.create")),
    db: Session = Depends(get_db),
):
    """Create a new note."""
    return crud.create_note(db, note, current_user.id)


@router.get("/", response_model=schemas.PaginatedNotesResponse)
def list_notes(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    category_id: Optional[UUID] = None,
    tag: Optional[str] = None,
    is_pinned: Optional[bool] = None,
    is_archived: Optional[bool] = None,
    is_favorite: Optional[bool] = None,
    current_user: User = Depends(require_permissions("notes.view")),
    db: Session = Depends(get_db),
):
    """List notes with filters and pagination."""
    skip = (page - 1) * size
    notes, total = crud.get_notes(
        db,
        current_user.id,
        skip=skip,
        limit=size,
        search=search,
        category_id=category_id,
        tag=tag,
        is_pinned=is_pinned,
        is_archived=is_archived,
        is_favorite=is_favorite,
    )
    
    # Convert to list response (with content preview)
    items = []
    for note in notes:
        # Create preview (first 150 chars of content without HTML)
        import re
        text = re.sub(r'<[^>]+>', '', note.content)
        preview = text[:150] + "..." if len(text) > 150 else text
        
        item_dict = {
            **note.__dict__,
            "content_preview": preview,
        }
        items.append(schemas.NoteListResponse(**item_dict))
    
    pages = (total + size - 1) // size
    
    return schemas.PaginatedNotesResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{note_id}", response_model=schemas.NoteResponse)
def get_note(
    note_id: UUID,
    current_user: User = Depends(require_permissions("notes.view")),
    db: Session = Depends(get_db),
):
    """Get a specific note."""
    note = crud.get_note(db, note_id, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=schemas.NoteResponse)
def update_note(
    note_id: UUID,
    note_update: schemas.NoteUpdate,
    current_user: User = Depends(require_permissions("notes.edit")),
    db: Session = Depends(get_db),
):
    """Update a note."""
    note = crud.update_note(db, note_id, note_update, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.delete("/{note_id}", status_code=204)
def delete_note(
    note_id: UUID,
    current_user: User = Depends(require_permissions("notes.delete")),
    db: Session = Depends(get_db),
):
    """Delete a note."""
    success = crud.delete_note(db, note_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return None


@router.post("/{note_id}/pin", response_model=schemas.NoteResponse)
def toggle_pin(
    note_id: UUID,
    current_user: User = Depends(require_permissions("notes.edit")),
    db: Session = Depends(get_db),
):
    """Toggle note pin status."""
    note = crud.get_note(db, note_id, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note.is_pinned = not note.is_pinned
    db.commit()
    db.refresh(note)
    return note


@router.post("/{note_id}/favorite", response_model=schemas.NoteResponse)
def toggle_favorite(
    note_id: UUID,
    current_user: User = Depends(require_permissions("notes.edit")),
    db: Session = Depends(get_db),
):
    """Toggle note favorite status."""
    note = crud.get_note(db, note_id, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note.is_favorite = not note.is_favorite
    db.commit()
    db.refresh(note)
    return note


@router.post("/{note_id}/archive", response_model=schemas.NoteResponse)
def toggle_archive(
    note_id: UUID,
    current_user: User = Depends(require_permissions("notes.edit")),
    db: Session = Depends(get_db),
):
    """Toggle note archive status."""
    note = crud.get_note(db, note_id, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note.is_archived = not note.is_archived
    db.commit()
    db.refresh(note)
    return note


@router.get("/tags/all", response_model=List[str])
def get_all_tags(
    current_user: User = Depends(require_permissions("notes.view")),
    db: Session = Depends(get_db),
):
    """Get all unique tags."""
    return crud.get_all_tags(db, current_user.id)
