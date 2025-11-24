'use client';

import { Pin, Star, Archive, MoreVertical, Calendar } from 'lucide-react';
import type { Note } from '@/types/notes';
import { formatDistanceToNow } from 'date-fns';

interface NoteCardProps {
  note: Note;
  onClick: () => void;
  onTogglePin: () => void;
  onToggleFavorite: () => void;
  onToggleArchive: () => void;
  onDelete: () => void;
}

export function NoteCard({
  note,
  onClick,
  onTogglePin,
  onToggleFavorite,
  onToggleArchive,
  onDelete,
}: NoteCardProps) {
  // Strip HTML tags for preview
  const contentPreview = note.content.replace(/<[^>]*>/g, '').substring(0, 150);

  return (
    <div
      onClick={onClick}
      className="group bg-white dark:bg-gray-800 border dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-semibold text-lg flex-1 line-clamp-2">{note.title}</h3>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onTogglePin();
            }}
            className={`p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 ${
              note.is_pinned ? 'text-blue-500' : 'text-gray-400'
            }`}
            title={note.is_pinned ? 'Unpin' : 'Pin'}
          >
            <Pin className="w-4 h-4" fill={note.is_pinned ? 'currentColor' : 'none'} />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleFavorite();
            }}
            className={`p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 ${
              note.is_favorite ? 'text-yellow-500' : 'text-gray-400'
            }`}
            title={note.is_favorite ? 'Unfavorite' : 'Favorite'}
          >
            <Star className="w-4 h-4" fill={note.is_favorite ? 'currentColor' : 'none'} />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleArchive();
            }}
            className={`p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 ${
              note.is_archived ? 'text-gray-500' : 'text-gray-400'
            }`}
            title={note.is_archived ? 'Unarchive' : 'Archive'}
          >
            <Archive className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content preview */}
      <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-3 mb-3">
        {contentPreview}
      </p>

      {/* Tags */}
      {note.tags && note.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {note.tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              className="inline-block px-2 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs"
            >
              {tag}
            </span>
          ))}
          {note.tags.length > 3 && (
            <span className="inline-block px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded text-xs">
              +{note.tags.length - 3}
            </span>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
        <div className="flex items-center gap-4">
          {note.category && (
            <span
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded"
              style={{
                backgroundColor: note.category.color ? `${note.category.color}20` : undefined,
                color: note.category.color || undefined,
              }}
            >
              {note.category.icon && <span>{note.category.icon}</span>}
              {note.category.name}
            </span>
          )}
          <span className="flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            {formatDistanceToNow(new Date(note.updated_at), { addSuffix: true })}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span>{note.word_count} words</span>
          <span>·</span>
          <span>{note.reading_time_minutes} min</span>
        </div>
      </div>
    </div>
  );
}
