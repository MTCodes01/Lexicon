'use client';

import { useState, useEffect } from 'react';
import { Plus, Loader2 } from 'lucide-react';
import { NoteSidebar } from '@/components/notes/note-sidebar';
import { SearchBar } from '@/components/notes/search-bar';
import { NoteCard } from '@/components/notes/note-card';
import { NoteEditorModal } from '@/components/notes/note-editor-modal';
import { CategoryModal } from '@/components/notes/category-modal';
import { notesApi, categoriesApi } from '@/utils/notes-api';
import type { Note, NoteCategory, NoteCreate, NoteUpdate, NoteCategoryCreate, NoteCategoryUpdate } from '@/types/notes';

export default function NotesPage() {
  // State
  const [notes, setNotes] = useState<Note[]>([]);
  const [categories, setCategories] = useState<NoteCategory[]>([]);
  const [tags, setTags] = useState<string[]>([]);
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Modals
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false);
  const [selectedNote, setSelectedNote] = useState<Note | undefined>();

  // Load initial data
  useEffect(() => {
    loadCategories();
    loadTags();
  }, []);

  // Load notes when filters change
  useEffect(() => {
    loadNotes();
  }, [selectedFilter, searchQuery, page]);

  const loadNotes = async () => {
    setIsLoading(true);
    try {
      const filters: any = {
        page,
        size: 20,
      };

      // Apply search
      if (searchQuery) {
        filters.search = searchQuery;
      }

      // Apply quick filters
      if (selectedFilter === 'pinned') {
        filters.is_pinned = true;
      } else if (selectedFilter === 'favorites') {
        filters.is_favorite = true;
      } else if (selectedFilter === 'archived') {
        filters.is_archived = true;
      } else if (selectedFilter.startsWith('category:')) {
        filters.category_id = selectedFilter.replace('category:', '');
      } else if (selectedFilter.startsWith('tag:')) {
        filters.tag = selectedFilter.replace('tag:', '');
      }

      const response = await notesApi.getNotes(filters);
      setNotes(response.items as any);
      setTotalPages(response.pages);
    } catch (error) {
      console.error('Failed to load notes:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const data = await categoriesApi.getCategories();
      setCategories(data || []);
    } catch (error) {
      console.error('Failed to load categories:', error);
      setCategories([]);
    }
  };

  const loadTags = async () => {
    try {
      const data = await notesApi.getAllTags();
      setTags(data || []);
    } catch (error) {
      console.error('Failed to load tags:', error);
      setTags([]);
    }
  };

  const handleCreateNote = () => {
    setSelectedNote(undefined);
    setIsEditorOpen(true);
  };

  const handleEditNote = (note: Note) => {
    setSelectedNote(note);
    setIsEditorOpen(true);
  };

  const handleSaveNote = async (data: NoteCreate | NoteUpdate) => {
    try {
      if (selectedNote) {
        await notesApi.updateNote(selectedNote.id, data as NoteUpdate);
      } else {
        await notesApi.createNote(data as NoteCreate);
      }
      await loadNotes();
      await loadTags();
      setIsEditorOpen(false);
    } catch (error) {
      console.error('Failed to save note:', error);
      throw error;
    }
  };

  const handleDeleteNote = async (noteId: string) => {
    if (!confirm('Are you sure you want to delete this note?')) return;

    try {
      await notesApi.deleteNote(noteId);
      await loadNotes();
    } catch (error) {
      console.error('Failed to delete note:', error);
    }
  };

  const handleTogglePin = async (noteId: string) => {
    try {
      await notesApi.togglePin(noteId);
      await loadNotes();
    } catch (error) {
      console.error('Failed to toggle pin:', error);
    }
  };

  const handleToggleFavorite = async (noteId: string) => {
    try {
      await notesApi.toggleFavorite(noteId);
      await loadNotes();
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  const handleToggleArchive = async (noteId: string) => {
    try {
      await notesApi.toggleArchive(noteId);
      await loadNotes();
    } catch (error) {
      console.error('Failed to toggle archive:', error);
    }
  };

  const handleSaveCategory = async (data: NoteCategoryCreate | NoteCategoryUpdate) => {
    try {
      await categoriesApi.createCategory(data as NoteCategoryCreate);
      await loadCategories();
      setIsCategoryModalOpen(false);
    } catch (error) {
      console.error('Failed to save category:', error);
      throw error;
    }
  };

  const handleTagClick = (tag: string) => {
    setSelectedFilter(`tag:${tag}`);
  };

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <NoteSidebar
        categories={categories}
        selectedFilter={selectedFilter}
        onFilterChange={setSelectedFilter}
        onCreateCategory={() => setIsCategoryModalOpen(true)}
        tags={tags}
        onTagClick={handleTagClick}
      />

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="border-b dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold">Notes</h1>
            <button
              onClick={handleCreateNote}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              <Plus className="w-4 h-4" />
              New Note
            </button>
          </div>
          <SearchBar
            value={searchQuery}
            onChange={setSearchQuery}
            onClear={() => setSearchQuery('')}
          />
        </div>

        {/* Notes grid */}
        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
            </div>
          ) : notes.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-gray-500 dark:text-gray-400">
              <p className="text-lg mb-2">No notes found</p>
              <p className="text-sm">Create your first note to get started!</p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {notes.map((note) => (
                  <NoteCard
                    key={note.id}
                    note={note}
                    onClick={() => handleEditNote(note)}
                    onTogglePin={() => handleTogglePin(note.id)}
                    onToggleFavorite={() => handleToggleFavorite(note.id)}
                    onToggleArchive={() => handleToggleArchive(note.id)}
                    onDelete={() => handleDeleteNote(note.id)}
                  />
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-center gap-2 mt-6">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 border dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    Page {page} of {totalPages}
                  </span>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="px-4 py-2 border dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Modals */}
      <NoteEditorModal
        isOpen={isEditorOpen}
        onClose={() => setIsEditorOpen(false)}
        note={selectedNote}
        categories={categories}
        onSave={handleSaveNote}
      />

      <CategoryModal
        isOpen={isCategoryModalOpen}
        onClose={() => setIsCategoryModalOpen(false)}
        categories={categories}
        onSave={handleSaveCategory}
      />
    </div>
  );
}
