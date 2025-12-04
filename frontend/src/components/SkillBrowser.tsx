/** Left panel: Master skills list with search. */
import React, { useState, useEffect, useMemo } from 'react';
import { useDraggable } from '@dnd-kit/core';
import { skillsApi, Skill } from '../services/api';

interface SkillBrowserProps {
  searchQuery: string;
  excludeSkillIds?: number[];  // Skill IDs to exclude from the list (already in existing/interested)
}

export const SkillBrowser: React.FC<SkillBrowserProps> = ({ searchQuery, excludeSkillIds = [] }) => {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadSkills();
  }, []);

  const loadSkills = async () => {
    try {
      setLoading(true);
      const data = await skillsApi.getAll();
      setSkills(data);
      setError(null);
      // Keep categories collapsed by default
      setExpandedCategories(new Set());
    } catch (err) {
      setError('Failed to load skills');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Filter skills based on search query and exclude already added skills
  const filteredSkills = skills.filter((skill) => {
    // Exclude if already in existing/interested lists
    if (excludeSkillIds.includes(skill.id)) {
      return false;
    }
    // Filter by search query (name, description, or category)
    const query = searchQuery.toLowerCase();
    return (
      skill.name.toLowerCase().includes(query) ||
      skill.description?.toLowerCase().includes(query) ||
      skill.category?.toLowerCase().includes(query)
    );
  });

  // Group skills by category
  const skillsByCategory = useMemo(() => {
    const grouped: Record<string, Skill[]> = {};
    filteredSkills.forEach((skill) => {
      const category = skill.category || 'Uncategorized';
      if (!grouped[category]) {
        grouped[category] = [];
      }
      grouped[category].push(skill);
    });
    return grouped;
  }, [filteredSkills]);

  const toggleCategory = (category: string) => {
    setExpandedCategories((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(category)) {
        newSet.delete(category);
      } else {
        newSet.add(category);
      }
      return newSet;
    });
  };

  if (loading) {
    return (
      <div className="p-4 text-center text-gray-500">Loading skills...</div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-center text-red-500">
        {error}
        <button
          onClick={loadSkills}
          className="ml-2 text-blue-600 hover:underline"
        >
          Retry
        </button>
      </div>
    );
  }

  const categories = Object.keys(skillsByCategory).sort();

  return (
    <div className="h-full max-h-[calc(100vh-180px)] overflow-y-auto">
      {filteredSkills.length === 0 ? (
        <div className="text-center text-gray-500 py-4 text-xs">
          {searchQuery ? 'No skills match your search' : 'No skills available'}
        </div>
      ) : (
        <div className="space-y-1">
          {categories.map((category) => {
            const categorySkills = skillsByCategory[category];
            const isExpanded = expandedCategories.has(category);
            
            return (
              <div key={category} className="border border-gray-200 rounded overflow-hidden">
                <button
                  onClick={() => toggleCategory(category)}
                  className="w-full px-2 py-1.5 bg-gray-50 hover:bg-gray-100 flex items-center justify-between transition-colors"
                >
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-semibold text-gray-700">{category}</span>
                    <span className="text-xs text-gray-500">({categorySkills.length})</span>
                  </div>
                  <svg
                    className={`w-3 h-3 text-gray-500 transition-transform ${isExpanded ? 'transform rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {isExpanded && (
                  <div className="p-1 space-y-1 bg-white">
                    {categorySkills.map((skill) => (
                      <DraggableSkillCard key={skill.id} skill={skill} />
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

/** Draggable skill card for master list. */
const DraggableSkillCard: React.FC<{ skill: Skill }> = ({ skill }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    isDragging,
  } = useDraggable({
    id: `skill-${skill.id}`,
    data: {
      type: 'skill',
      skill,
    },
  });

  const style = transform
    ? {
        transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
        opacity: isDragging ? 0.5 : 1,
      }
    : undefined;

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className={`
        bg-white rounded shadow-sm p-1.5 cursor-grab active:cursor-grabbing
        border border-gray-200 hover:border-blue-400 hover:shadow-md transition-all
        ${isDragging ? 'shadow-lg ring-2 ring-blue-400 opacity-50' : ''}
      `}
      role="button"
      tabIndex={0}
      aria-label={`Drag skill: ${skill.name}`}
      onKeyDown={(e) => {
        if (e.key === ' ' || e.key === 'Enter') {
          e.preventDefault();
        }
      }}
    >
      <div className="flex items-start gap-1.5">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-3 h-3 text-gray-400 flex-shrink-0 mt-0.5">
          <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
        </svg>
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-gray-800 text-xs">{skill.name}</h3>
          {skill.description && (
            <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">{skill.description}</p>
          )}
        </div>
      </div>
    </div>
  );
};

