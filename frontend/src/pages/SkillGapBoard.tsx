/** Skill Gap Board - Display skills with gaps from band requirements. */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi, bandsApi, BandAnalysis, SkillGap } from '../services/api';


export const SkillGapBoard: React.FC = () => {
  const [analysis, setAnalysis] = useState<BandAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'below' | 'at' | 'above'>('all');
  const navigate = useNavigate();
  const user = authApi.getUser();

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    loadBandAnalysis();
  }, []);

  const loadBandAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await bandsApi.getMyAnalysis();
      setAnalysis(data);
    } catch (err) {
      console.error('Failed to load band analysis:', err);
      setError(err instanceof Error ? err.message : 'Failed to load band analysis');
    } finally {
      setLoading(false);
    }
  };

  const getGapColor = (gap: number) => {
    if (gap > 0) {
      return 'bg-green-100 text-green-800'; // Above requirement
    } else if (gap === 0) {
      return 'bg-gray-100 text-gray-800'; // At requirement
    } else {
      return 'bg-yellow-100 text-yellow-800'; // Below requirement
    }
  };

  const getRatingColor = (rating?: string) => {
    switch (rating) {
      case 'Expert':
        return 'bg-purple-100 text-purple-800';
      case 'Advanced':
        return 'bg-orange-100 text-orange-800';
      case 'Intermediate':
        return 'bg-yellow-100 text-yellow-800';
      case 'Developing':
        return 'bg-blue-100 text-blue-800';
      case 'Beginner':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const filteredGaps = analysis?.skill_gaps.filter((gap) => {
    if (filter === 'below') return gap.gap < 0;
    if (filter === 'at') return gap.gap === 0;
    if (filter === 'above') return gap.gap > 0;
    return true;
  }) || [];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl text-gray-600">Loading skill gap analysis...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl text-red-600 mb-4">Error: {error}</div>
          <button
            onClick={loadBandAnalysis}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl text-gray-600">No analysis data available</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">Skill Gap Analysis</h1>
          <div className="flex gap-2 items-center">
            <span className="text-sm text-gray-600">{user?.email}</span>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Back to Dashboard
            </button>
            <button
              onClick={() => authApi.logout() && navigate('/login')}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Summary Card */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div>
              <div className="text-sm text-gray-600">Employee</div>
              <div className="text-lg font-semibold">{analysis.employee_name}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Band</div>
              <div className="text-lg font-semibold text-blue-600">{analysis.band}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Average Rating</div>
              <div className="text-lg font-semibold">{analysis.average_rating.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Total Skills</div>
              <div className="text-lg font-semibold">{analysis.total_skills}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Skills Below</div>
              <div className="text-lg font-semibold text-yellow-600">{analysis.skills_below_requirement}</div>
            </div>
          </div>
        </div>

        {/* Filter Buttons */}
        <div className="mb-4 flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filter === 'all' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            All ({analysis.skill_gaps.length})
          </button>
          <button
            onClick={() => setFilter('below')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filter === 'below' ? 'bg-yellow-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Below Requirement ({analysis.skills_below_requirement})
          </button>
          <button
            onClick={() => setFilter('at')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filter === 'at' ? 'bg-gray-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            At Requirement ({analysis.skills_at_requirement})
          </button>
          <button
            onClick={() => setFilter('above')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filter === 'above' ? 'bg-green-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Above Requirement ({analysis.skills_above_requirement})
          </button>
        </div>

        {/* Skill Gap Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-green-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider bg-black text-white">
                    Skill
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Level (Textual)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Level (Numerical)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Role Requirement ({analysis.band})
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Level (Numerical)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    G
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredGaps.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                      No skills found for the selected filter.
                    </td>
                  </tr>
                ) : (
                  filteredGaps.map((gap) => (
                    <tr key={gap.skill_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap bg-black text-white font-medium">
                        {gap.skill_name}
                        {gap.skill_category && (
                          <span className="ml-2 text-xs text-gray-300">({gap.skill_category})</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {gap.current_rating_text ? (
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getRatingColor(gap.current_rating_text)}`}>
                            {gap.current_rating_text}
                          </span>
                        ) : (
                          <span className="text-gray-400 text-xs">Not assessed</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {gap.current_rating_number ?? '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getRatingColor(gap.required_rating_text)}`}>
                          {gap.required_rating_text}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {gap.required_rating_number}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getGapColor(gap.gap)}`}>
                        {gap.gap > 0 ? `+${gap.gap}` : gap.gap}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

