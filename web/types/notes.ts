/**
 * TypeScript types for Notes module
 */

export interface Note {
  id: string;
  user_id: string;
  title: string;
  content: string;
  content_type: 'html' | 'markdown' | 'plain';
  category_id?: string;
  category?: NoteCategory;
  tags: string[];
  is_pinned: boolean;
  is_archived: boolean;
  is_favorite: boolean;
  word_count: number;
  character_count: number;
  reading_time_minutes: number;
  created_at: string;
  updated_at: string;
  last_viewed_at?: string;
}

export interface NoteCategory {
  id: string;
  user_id: string;
  name: string;
  color?: string;
  icon?: string;
  description?: string;
  parent_id?: string;
  children?: NoteCategory[];
  created_at: string;
  updated_at: string;
}

export interface NoteVersion {
  id: string;
  note_id: string;
  title: string;
  content: string;
  version_number: number;
  created_at: string;
  created_by: string;
}

export interface NoteCreate {
  title: string;
  content: string;
  content_type?: 'html' | 'markdown' | 'plain';
  category_id?: string;
  tags?: string[];
}

export interface NoteUpdate {
  title?: string;
  content?: string;
  content_type?: 'html' | 'markdown' | 'plain';
  category_id?: string;
  tags?: string[];
}

export interface NoteCategoryCreate {
  name: string;
  color?: string;
  icon?: string;
  description?: string;
  parent_id?: string;
}

export interface NoteCategoryUpdate {
  name?: string;
  color?: string;
  icon?: string;
  description?: string;
  parent_id?: string;
}

export interface NotesFilter {
  search?: string;
  category_id?: string;
  tag?: string;
  is_pinned?: boolean;
  is_archived?: boolean;
  is_favorite?: boolean;
  page?: number;
  size?: number;
}

export interface PaginatedNotesResponse {
  items: Note[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface NoteListItem extends Omit<Note, 'content'> {
  content_preview: string;
}
