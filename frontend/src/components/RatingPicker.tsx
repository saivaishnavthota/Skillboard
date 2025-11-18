/** Rating picker component for selecting skill rating with icons. */
import React from 'react';

export type Rating = 'Beginner' | 'Developing' | 'Intermediate' | 'Advanced' | 'Expert';

interface RatingPickerProps {
  value: Rating;
  onChange: (rating: Rating) => void;
}

// Icon components for each rating level
const BeginnerIcon = () => (
  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
    <circle cx="10" cy="10" r="8" fill="none" stroke="currentColor" strokeWidth="2"/>
    <circle cx="10" cy="10" r="3" fill="currentColor"/>
  </svg>
);

const DevelopingIcon = () => (
  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
    <path d="M10 2 L10 18 M2 10 L18 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
    <circle cx="10" cy="10" r="6" fill="none" stroke="currentColor" strokeWidth="2"/>
  </svg>
);

const IntermediateIcon = () => (
  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
    <path d="M10 2 L10 18 M2 10 L18 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
    <path d="M10 2 L2 10 L10 18 L18 10 Z" fill="none" stroke="currentColor" strokeWidth="2"/>
  </svg>
);

const AdvancedIcon = () => (
  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
    <path d="M10 2 L10 18 M2 10 L18 10 M10 2 L2 10 L10 18 L18 10 Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" fill="none"/>
    <circle cx="10" cy="10" r="2" fill="currentColor"/>
  </svg>
);

const ExpertIcon = () => (
  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
    <path d="M10 2 L10 18 M2 10 L18 10 M10 2 L2 10 L10 18 L18 10 Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" fill="none"/>
    <circle cx="10" cy="10" r="3" fill="currentColor"/>
    <circle cx="10" cy="10" r="1" fill="white"/>
  </svg>
);

const ratingIcons = {
  Beginner: BeginnerIcon,
  Developing: DevelopingIcon,
  Intermediate: IntermediateIcon,
  Advanced: AdvancedIcon,
  Expert: ExpertIcon,
};

const ratingColors = {
  Beginner: 'bg-green-100 text-green-800 border-green-300',
  Developing: 'bg-blue-100 text-blue-800 border-blue-300',
  Intermediate: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  Advanced: 'bg-orange-100 text-orange-800 border-orange-300',
  Expert: 'bg-purple-100 text-purple-800 border-purple-300',
};

const ratingTooltips = {
  Beginner: 'New to the skill; limited or no practical experience',
  Developing: 'Gaining confidence and consistency in applying the skill',
  Intermediate: 'Competent and reliable in using the skill independently',
  Advanced: 'Deep understanding and consistent high performance',
  Expert: 'Recognised authority in the skill area',
};

export const RatingPicker: React.FC<RatingPickerProps> = ({ value, onChange }) => {
  const ratings: Rating[] = ['Beginner', 'Developing', 'Intermediate', 'Advanced', 'Expert'];

  const handleKeyDown = (e: React.KeyboardEvent, rating: Rating) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onChange(rating);
    }
    // Arrow keys for cycling through ratings
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
      e.preventDefault();
      const currentIndex = ratings.indexOf(value);
      const nextIndex = (currentIndex + 1) % ratings.length;
      onChange(ratings[nextIndex]);
    }
    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      e.preventDefault();
      const currentIndex = ratings.indexOf(value);
      const prevIndex = (currentIndex - 1 + ratings.length) % ratings.length;
      onChange(ratings[prevIndex]);
    }
  };

  return (
    <div className="flex gap-1" role="radiogroup" aria-label="Skill rating">
      {ratings.map((rating) => {
        const IconComponent = ratingIcons[rating];
        return (
          <button
            key={rating}
            type="button"
            onClick={() => onChange(rating)}
            onKeyDown={(e) => handleKeyDown(e, rating)}
            className={`
              px-2 py-1 text-xs font-medium rounded border transition-colors
              flex items-center gap-1
              ${value === rating
                ? `${ratingColors[rating]} border-2 font-bold`
                : 'bg-gray-100 text-gray-600 border-gray-300 hover:bg-gray-200'
              }
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1
            `}
            aria-checked={value === rating}
            role="radio"
            tabIndex={value === rating ? 0 : -1}
            title={ratingTooltips[rating]}
          >
            <IconComponent />
            <span className="hidden sm:inline">{rating.charAt(0)}</span>
          </button>
        );
      })}
    </div>
  );
};

