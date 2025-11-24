/**
 * API client for Notes module
 */
import { apiClient } from '@/lib/api-client';
import type {
  Note,
  NoteCategory,
  NoteCreate,
  NoteUpdate,
  NoteCategoryCreate,
  NoteCategoryUpdate,
  NotesFilter,
  PaginatedNotesResponse,
} from '@/types/notes';

// Notes endpoints
export const notesApi = {
  // Get all notes with filters
  getNotes: async (filters?: NotesFilter): Promise<PaginatedNotesResponse> => {
    const params = new URLSearchParams();
    if (filters?.search) params.append('search', filters.search);
    if (filters?.category_id) params.append('category_id', filters.category_id);
    if (filters?.tag) params.append('tag', filters.tag);
    if (filters?.is_pinned !== undefined) params.append('is_pinned', String(filters.is_pinned));
    if (filters?.is_archived !== undefined) params.append('is_archived', String(filters.is_archived));
    if (filters?.is_favorite !== undefined) params.append('is_favorite', String(filters.is_favorite));
    if (filters?.page) params.append('page', String(filters.page));
    if (filters?.size) params.append('size', String(filters.size));

    const response = await apiClient.get(`/notes?${params.toString()}`);
    return response.data;
  },

  // Get a single note
  getNote: async (id: string): Promise<Note> => {
    const response = await apiClient.get(`/notes/${id}`);
    return response.data;
  },

  // Create a new note
  createNote: async (data: NoteCreate): Promise<Note> => {
    const response = await apiClient.post('/notes', data);
    return response.data;
  },

  // Update a note
  updateNote: async (id: string, data: NoteUpdate): Promise<Note> => {
    const response = await apiClient.put(`/notes/${id}`, data);
    return response.data;
  },

  // Delete a note
  deleteNote: async (id: string): Promise<void> => {
    await apiClient.delete(`/notes/${id}`);
  },

  // Toggle pin status
  togglePin: async (id: string): Promise<Note> => {
    const response = await apiClient.post(`/notes/${id}/pin`);
    return response.data;
  },

  // Toggle favorite status
  toggleFavorite: async (id: string): Promise<Note> => {
    const response = await apiClient.post(`/notes/${id}/favorite`);
    return response.data;
  },

  // Toggle archive status
  toggleArchive: async (id: string): Promise<Note> => {
    const response = await apiClient.post(`/notes/${id}/archive`);
    return response.data;
  },

  // Get all tags
  getAllTags: async (): Promise<string[]> => {
    const response = await apiClient.get('/notes/tags/all');
    return response.data;
  },
};

// Categories endpoints
export const categoriesApi = {
  // Get all categories
  getCategories: async (): Promise<NoteCategory[]> => {
    const response = await apiClient.get('/notes/categories');
    return response.data;
  },

  // Get a single category
  getCategory: async (id: string): Promise<NoteCategory> => {
    const response = await apiClient.get(`/notes/categories/${id}`);
    return response.data;
  },

  // Create a new category
  createCategory: async (data: NoteCategoryCreate): Promise<NoteCategory> => {
    const response = await apiClient.post('/notes/categories', data);
    return response.data;
  },

  // Update a category
  updateCategory: async (id: string, data: NoteCategoryUpdate): Promise<NoteCategory> => {
    const response = await apiClient.put(`/notes/categories/${id}`, data);
    return response.data;
  },

  // Delete a category
  deleteCategory: async (id: string): Promise<void> => {
    await apiClient.delete(`/notes/categories/${id}`);
  },
};
