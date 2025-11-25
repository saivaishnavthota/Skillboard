/** Skill card component for drag-and-drop. */
import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { useDroppable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import { RatingPicker } from './RatingPicker';

export interface SkillCardData {
  id: number;  // skill_id
  employee_skill_id?: number;  // employee_skill.id for updates
  name: string;
  description?: string;
  rating?: 'Beginner' | 'Developing' | 'Intermediate' | 'Advanced' | 'Expert';
  years_experience?: number;
}

interface SkillCardProps {
  skill: SkillCardData;
  onRatingChange?: (skillId: number, rating: 'Beginner' | 'Developing' | 'Intermediate' | 'Advanced' | 'Expert') => void;
  showRating?: boolean;
  columnType?: 'existing' | 'interested';
  onRemove?: () => void;
  showRemove?: boolean;
}

export const SkillCard: React.FC<SkillCardProps> = ({
  skill,
  onRatingChange,
  showRating = false,
  columnType,
  onRemove,
  showRemove = false,
}) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: skill.id });

  // Also make this card a droppable target for skills from master list
  const { setNodeRef: setDroppableRef, isOver } = useDroppable({
    id: `${columnType}-${skill.id}`,
  });

  // Combine both refs
  const combinedRef = (node: HTMLDivElement | null) => {
    setNodeRef(node);
    setDroppableRef(node);
  };

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const handleRatingChange = (rating: 'Beginner' | 'Developing' | 'Intermediate' | 'Advanced' | 'Expert') => {
    if (onRatingChange) {
      onRatingChange(skill.id, rating);
    }
  };

  return (
    <div
      ref={combinedRef}
      style={style}
      {...attributes}
      {...listeners}
      className={`
        bg-white rounded-lg shadow-md p-4 mb-2 cursor-grab active:cursor-grabbing relative
        border-2 transition-colors
        ${isDragging ? 'shadow-lg border-blue-400' : isOver ? 'border-blue-400 bg-blue-50' : 'border-gray-200 hover:border-blue-400'}
      `}
      role="button"
      tabIndex={0}
      aria-label={`Skill: ${skill.name}`}
      onKeyDown={(e) => {
        // Keyboard navigation: Space or Enter to start drag
        if (e.key === ' ' || e.key === 'Enter') {
          e.preventDefault();
          // Trigger drag programmatically if needed
        }
        // Arrow keys for reordering (handled by parent)
        if (['ArrowUp', 'ArrowDown'].includes(e.key)) {
          e.preventDefault();
        }
      }}
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h3 className="font-semibold text-gray-800">{skill.name}</h3>
          {skill.description && (
            <p className="text-sm text-gray-600 mt-1">{skill.description}</p>
          )}
          {skill.years_experience !== undefined && skill.years_experience !== null && (
            <p className="text-xs text-gray-500 mt-1" title="Years of experience: How many years you have been working with this skill">
              {skill.years_experience} {skill.years_experience === 1 ? 'year' : 'years'} of experience
            </p>
          )}
        </div>
        <div className="ml-4">
          {showRating && (
            <div>
              <RatingPicker
                value={skill.rating || 'Beginner'}
                onChange={handleRatingChange}
              />
            </div>
          )}
        </div>
      </div>
      {onRemove && showRemove && (
        <button
          type="button"
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); onRemove(); }}
          onPointerDown={(e) => { e.stopPropagation(); }}
          onMouseDown={(e) => { e.stopPropagation(); }}
          className="absolute -top-2 -right-2 z-20 p-1 rounded-full bg-white hover:bg-gray-100 border border-gray-300 shadow"
          aria-label="Remove skill"
          title="Remove skill"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4 text-gray-700">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      )}
    </div>
  );
};

