/** Fuzzy search results component. */
import React from 'react';
import { FuzzySearchResult } from '../services/api';

interface FuzzySearchResultsProps {
  results: FuzzySearchResult[];
  threshold: number;
}

export const FuzzySearchResults: React.FC<FuzzySearchResultsProps> = ({
  results,
  threshold,
}) => {
  if (results.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No employees found matching the search criteria (threshold: {threshold}%)
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {results.map((result, idx) => (
        <div
          key={idx}
          className="bg-white rounded-lg shadow-md p-4 border border-gray-200"
        >
          <div className="flex justify-between items-start mb-2">
            <div>
              <h3 className="font-semibold text-lg text-gray-800">
                {result.employee_name}
              </h3>
              <p className="text-sm text-gray-600">ID: {result.employee_id}</p>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-blue-600">
                {result.overall_match_score.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500">Match Score</div>
            </div>
          </div>

          {/* Matched skills */}
          <div className="mt-3">
            <p className="text-sm font-medium text-gray-700 mb-2">
              Matched Skills:
            </p>
            <div className="flex flex-wrap gap-2">
              {result.matched_skills.map((matched, skillIdx) => (
                <span
                  key={skillIdx}
                  className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm"
                >
                  {matched.skill_name} ({matched.match_score.toFixed(0)}%)
                </span>
              ))}
            </div>
          </div>

          {/* All skills with ratings */}
          <div className="mt-3 pt-3 border-t border-gray-200">
            <p className="text-sm font-medium text-gray-700 mb-2">
              All Skills:
            </p>
            <div className="space-y-1">
              {result.ratings.map((rating, ratingIdx) => (
                <div
                  key={ratingIdx}
                  className="flex justify-between items-center text-sm"
                >
                  <span className="text-gray-700">{rating.skill_name}</span>
                  <div className="flex items-center gap-2">
                    <span
                      className={`
                        px-2 py-0.5 rounded text-xs font-medium
                        ${
                          rating.rating === 'Expert'
                            ? 'bg-purple-100 text-purple-800'
                            : rating.rating === 'Advanced'
                            ? 'bg-orange-100 text-orange-800'
                            : rating.rating === 'Intermediate'
                            ? 'bg-yellow-100 text-yellow-800'
                            : rating.rating === 'Developing'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-green-100 text-green-800'
                        }
                      `}
                    >
                      {rating.rating}
                    </span>
                    {rating.years_experience !== undefined && (
                      <span className="text-gray-500 text-xs">
                        {rating.years_experience} yrs
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

