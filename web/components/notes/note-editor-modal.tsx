'use client';

import { useState, useEffect, useCallback } from 'react';
import { X, Save, Loader2 } from 'lucide-react';
import { TiptapEditor } from './tiptap-editor';
import type { Note, NoteCreate, NoteUpdate, NoteCategory } from '@/types/notes';

interface NoteEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  note?: Note;
  categories: NoteCategory[];
  onSave: (data: NoteCreate | NoteUpdate) => Promise<void>;
}

export function NoteEditorModal({ isOpen, onClose, note, categories, onSave }: NoteEditorModalProps) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [categoryId, setCategoryId] = useState<string>('');
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // Initialize form with note data
  useEffect(() => {
    if (note) {
      setTitle(note.title);
      setContent(note.content || '');
      setCategoryId(note.category_id || '');
      setTags(note.tags || []);
    } else {
      setTitle('');
      setContent('');
      setCategoryId('');
      setTags([]);
    }
    setHasChanges(false);
  }, [note, isOpen]);

  // Auto-save debounced
  useEffect(() => {
    if (!hasChanges || !title) return;

    const timer = setTimeout(() => {
      handleSave();
    }, 2000);

    return () => clearTimeout(timer);
  }, [title, content, categoryId, tags, hasChanges]);

  const handleSave = async () => {
    if (!title.trim()) return;

    setIsSaving(true);
    try {
      const data: NoteCreate | NoteUpdate = {
        title: title.trim(),
        content,
        content_type: 'html',
        category_id: categoryId || undefined,
        tags,
      };

      await onSave(data);
      setHasChanges(false);
      onClose();
    } catch (error) {
      console.error('Failed to save note:', error);
      alert('Failed to save note. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddTag = () => {
    const tag = tagInput.trim();
    if (tag && !tags.includes(tag)) {
      setTags([...tags, tag]);
      setTagInput('');
      setHasChanges(true);
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(t => t !== tagToRemove));
    setHasChanges(true);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  if (!isOpen) return null;

  // Calculate metadata
  const wordCount = (content || '').replace(/<[^>]*>/g, '').split(/\s+/).filter(Boolean).length;
  const charCount = (content || '').replace(/<[^>]*>/g, '').length;
  const readingTime = Math.ceil(wordCount / 200);

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-5xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
          <div className="flex items-center gap-2 flex-1">
            <input
              type="text"
              value={title}
              onChange={(e) => {
                setTitle(e.target.value);
                setHasChanges(true);
              }}
              placeholder="Note title..."
              className="text-2xl font-bold bg-transparent border-none focus:outline-none flex-1"
              autoFocus
            />
            {isSaving && <Loader2 className="w-5 h-5 animate-spin text-gray-400" />}
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Metadata bar */}
        <div className="flex items-center gap-4 px-4 py-2 border-b dark:border-gray-700 text-sm text-gray-600 dark:text-gray-400">
          <select
            value={categoryId}
            onChange={(e) => {
              setCategoryId(e.target.value);
              setHasChanges(true);
            }}
            className="bg-transparent border border-gray-300 dark:border-gray-600 rounded px-2 py-1"
          >
            <option value="">No category</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>

          <div className="flex items-center gap-2 flex-1">
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Add tags..."
              className="bg-transparent border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-sm flex-1"
            />
            <button
              onClick={handleAddTag}
              className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
            >
              Add
            </button>
          </div>

          <div className="flex items-center gap-2">
            <span>{wordCount} words</span>
            <span>·</span>
            <span>{charCount} chars</span>
            <span>·</span>
            <span>{readingTime} min read</span>
          </div>
        </div>

        {/* Tags */}
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-2 px-4 py-2 border-b dark:border-gray-700">
            {tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-sm"
              >
                {tag}
                <button
                  onClick={() => handleRemoveTag(tag)}
                  className="hover:text-blue-600 dark:hover:text-blue-400"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        )}

        {/* Editor */}
        <div className="flex-1 overflow-auto p-4">
          <TiptapEditor
            content={content}
            onChange={(newContent) => {
              setContent(newContent);
              setHasChanges(true);
            }}
          />
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t dark:border-gray-700">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            {hasChanges ? 'Unsaved changes' : 'All changes saved'}
          </div>
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              Close
            </button>
            <button
              onClick={handleSave}
              disabled={!title.trim() || isSaving}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              {isSaving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
