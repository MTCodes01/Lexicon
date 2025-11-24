'use client';

import { FileText, Pin, Star, Archive, Folder, Plus, Tag } from 'lucide-react';
import type { NoteCategory } from '@/types/notes';

interface NoteSidebarProps {
  categories: NoteCategory[];
  selectedFilter: string;
  onFilterChange: (filter: string) => void;
  onCreateCategory: () => void;
  tags: string[];
  onTagClick: (tag: string) => void;
}

export function NoteSidebar({
  categories,
  selectedFilter,
  onFilterChange,
  onCreateCategory,
  tags,
  onTagClick,
}: NoteSidebarProps) {
  const filters = [
    { id: 'all', label: 'All Notes', icon: FileText },
    { id: 'pinned', label: 'Pinned', icon: Pin },
    { id: 'favorites', label: 'Favorites', icon: Star },
    { id: 'archived', label: 'Archived', icon: Archive },
  ];

  return (
    <div className="w-64 border-r dark:border-gray-700 bg-white dark:bg-gray-800 p-4 overflow-y-auto">
      {/* Quick filters */}
      <div className="mb-6">
        <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">
          Quick Access
        </h3>
        <div className="space-y-1">
          {filters.map((filter) => {
            const Icon = filter.icon;
            return (
              <button
                key={filter.id}
                onClick={() => onFilterChange(filter.id)}
                className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                  selectedFilter === filter.id
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                {filter.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Categories */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">
            Categories
          </h3>
          <button
            onClick={onCreateCategory}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            title="Create category"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
        <div className="space-y-1">
          {categories.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-400 px-3 py-2">
              No categories yet
            </p>
          ) : (
            categories.map((category) => (
              <button
                key={category.id}
                onClick={() => onFilterChange(`category:${category.id}`)}
                className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                  selectedFilter === `category:${category.id}`
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <Folder
                  className="w-4 h-4"
                  style={{ color: category.color || undefined }}
                />
                <span className="flex-1 text-left truncate">{category.name}</span>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Tags */}
      {tags.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">
            Tags
          </h3>
          <div className="flex flex-wrap gap-1">
            {tags.slice(0, 10).map((tag) => (
              <button
                key={tag}
                onClick={() => onTagClick(tag)}
                className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded text-xs transition-colors"
              >
                <Tag className="w-3 h-3" />
                {tag}
              </button>
            ))}
            {tags.length > 10 && (
              <span className="inline-block px-2 py-1 text-xs text-gray-500 dark:text-gray-400">
                +{tags.length - 10} more
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
