/** Employee Learning Platform - View and complete assigned courses. */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi, learningApi, CourseAssignment } from '../services/api';
import NxzenLogo from '../images/Nxzen.jpg';

export const EmployeeLearning: React.FC = () => {
  const [assignments, setAssignments] = useState<CourseAssignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'not-started' | 'in-progress' | 'completed'>('all');
  const [selectedAssignment, setSelectedAssignment] = useState<CourseAssignment | null>(null);
  const [certificateFile, setCertificateFile] = useState<File | null>(null);
  const [notes, setNotes] = useState('');
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();
  const user = authApi.getUser();

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    loadAssignments();
  }, []);

  const loadAssignments = async () => {
    try {
      setLoading(true);
      const data = await learningApi.getMyAssignments();
      setAssignments(data);
    } catch (error) {
      console.error('Failed to load assignments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartCourse = async (assignmentId: number) => {
    try {
      await learningApi.startCourse(assignmentId);
      loadAssignments();
    } catch (error) {
      console.error('Failed to start course:', error);
    }
  };

  const handleCompleteCourse = async () => {
    if (!selectedAssignment) return;

    try {
      setUploading(true);
      await learningApi.completeCourse(selectedAssignment.id, certificateFile || undefined, notes || undefined);
      setSelectedAssignment(null);
      setCertificateFile(null);
      setNotes('');
      loadAssignments();
    } catch (error) {
      console.error('Failed to complete course:', error);
    } finally {
      setUploading(false);
    }
  };

  const filteredAssignments = assignments.filter((assignment) => {
    if (filter === 'not-started') return assignment.status === 'Not Started';
    if (filter === 'in-progress') return assignment.status === 'In Progress';
    if (filter === 'completed') return assignment.status === 'Completed';
    return true;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Completed':
        return 'bg-green-100 text-green-800';
      case 'In Progress':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const mandatoryCount = assignments.filter(a => a.status !== 'Completed').length;

  return (
    <div className="min-h-screen bg-[#F6F2F4]">
      <header className="bg-[#F6F2F4] shadow-sm border-b border-gray-200">
        <div className="w-full px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <img src={NxzenLogo} alt="Nxzen" className="h-8 w-8 object-cover" />
            <span className="text-xl font-semibold text-gray-800">nxzen</span>
            <span aria-hidden className="h-6 w-px bg-gray-300" />
            <h1 className="text-2xl font-bold text-gray-800 italic">My Learning</h1>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate('/skill-gap')}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              Back to Profile
            </button>
            <button
              onClick={() => { authApi.logout(); navigate('/login'); }}
              className="p-2 rounded-lg hover:bg-gray-200"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5 text-red-600">
                <path d="M16 13v-2H7V8l-5 4 5 4v-3h9zm3-11H9c-1.1 0-2 .9-2 2v3h2V4h10v16H9v-2H7v3c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* Quick Actions / Navigation */}
        <div className="mb-6">
          <h2 className="text-center text-xl font-semibold text-gray-800 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-4 p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all bg-white"
            >
              <div className="flex-shrink-0 w-14 h-14 rounded-xl flex items-center justify-center bg-gray-50">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-7 h-7 text-gray-700">
                  <path fillRule="evenodd" d="M7.5 6a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM3.751 20.105a8.25 8.25 0 0116.498 0 .75.75 0 01-.437.695A18.683 18.683 0 0112 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 01-.437-.695z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="text-left">
                <div className="text-base font-semibold text-gray-900">My Profile</div>
                <div className="text-sm text-gray-500">View your details</div>
              </div>
            </button>

            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-4 p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all bg-white"
            >
              <div className="flex-shrink-0 w-14 h-14 rounded-xl flex items-center justify-center bg-green-50">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-7 h-7 text-green-700">
                  <path fillRule="evenodd" d="M2.25 13.5a8.25 8.25 0 018.25-8.25.75.75 0 01.75.75v6.75H18a.75.75 0 01.75.75 8.25 8.25 0 01-16.5 0z" clipRule="evenodd" />
                  <path fillRule="evenodd" d="M12.75 3a.75.75 0 01.75-.75 8.25 8.25 0 018.25 8.25.75.75 0 01-.75.75h-7.5a.75.75 0 01-.75-.75V3z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="text-left">
                <div className="text-base font-semibold text-gray-900">Career Engagement</div>
                <div className="text-sm text-gray-500">Track your progress</div>
              </div>
            </button>

            <button
              className="flex items-center gap-4 p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all bg-white ring-2 ring-blue-500 relative"
            >
              <div className="flex-shrink-0 w-14 h-14 rounded-xl flex items-center justify-center bg-blue-50">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-7 h-7 text-blue-700">
                  <path d="M11.7 2.805a.75.75 0 01.6 0A60.65 60.65 0 0122.83 8.72a.75.75 0 01-.231 1.337 49.949 49.949 0 00-9.902 3.912l-.003.002-.34.18a.75.75 0 01-.707 0A50.009 50.009 0 007.5 12.174v-.224c0-.131.067-.248.172-.311a54.614 54.614 0 014.653-2.52.75.75 0 00-.65-1.352 56.129 56.129 0 00-4.78 2.589 1.858 1.858 0 00-.859 1.228 49.803 49.803 0 00-4.634-1.527.75.75 0 01-.231-1.337A60.653 60.653 0 0111.7 2.805z" />
                  <path d="M13.06 15.473a48.45 48.45 0 017.666-3.282c.134 1.414.22 2.843.255 4.285a.75.75 0 01-.46.71 47.878 47.878 0 00-8.105 4.342.75.75 0 01-.832 0 47.877 47.877 0 00-8.104-4.342.75.75 0 01-.461-.71c.035-1.442.121-2.87.255-4.286A48.4 48.4 0 016 13.18v1.27a1.5 1.5 0 00-.14 2.508c-.09.38-.222.753-.397 1.11.452.213.901.434 1.346.661a6.729 6.729 0 00.551-1.608 1.5 1.5 0 00.14-2.67v-.645a48.549 48.549 0 013.44 1.668 2.25 2.25 0 002.12 0z" />
                  <path d="M4.462 19.462c.42-.419.753-.89 1-1.394.453.213.902.434 1.347.661a6.743 6.743 0 01-1.286 1.794.75.75 0 11-1.06-1.06z" />
                </svg>
              </div>
              <div className="text-left">
                <div className="text-base font-semibold text-gray-900">Mandatory Learning</div>
                <div className="text-sm text-gray-500">Complete courses</div>
              </div>
              {mandatoryCount > 0 && (
                <span className="absolute top-2 right-2 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
                  {mandatoryCount}
                </span>
              )}
            </button>
          </div>
        </div>

        {/* Summary Card */}
        {mandatoryCount > 0 && (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-yellow-700">
                  You have <strong>{mandatoryCount}</strong> pending course{mandatoryCount !== 1 ? 's' : ''} to complete.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Filter Buttons */}
        <div className="mb-6 flex gap-3">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg font-medium ${
              filter === 'all' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 border border-gray-300'
            }`}
          >
            All ({assignments.length})
          </button>
          <button
            onClick={() => setFilter('not-started')}
            className={`px-4 py-2 rounded-lg font-medium ${
              filter === 'not-started' ? 'bg-gray-600 text-white' : 'bg-white text-gray-700 border border-gray-300'
            }`}
          >
            Not Started ({assignments.filter(a => a.status === 'Not Started').length})
          </button>
          <button
            onClick={() => setFilter('in-progress')}
            className={`px-4 py-2 rounded-lg font-medium ${
              filter === 'in-progress' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 border border-gray-300'
            }`}
          >
            In Progress ({assignments.filter(a => a.status === 'In Progress').length})
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={`px-4 py-2 rounded-lg font-medium ${
              filter === 'completed' ? 'bg-green-600 text-white' : 'bg-white text-gray-700 border border-gray-300'
            }`}
          >
            Completed ({assignments.filter(a => a.status === 'Completed').length})
          </button>
        </div>

        {/* Courses List */}
        {loading ? (
          <div className="text-center py-12 text-gray-500">Loading courses...</div>
        ) : filteredAssignments.length === 0 ? (
          <div className="text-center py-12 text-gray-500 bg-white rounded-lg">
            No courses found for the selected filter.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAssignments.map((assignment) => (
              <div key={assignment.id} className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-bold text-gray-900">{assignment.course_title}</h3>
                  <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(assignment.status)}`}>
                    {assignment.status}
                  </span>
                </div>

                {assignment.due_date && (
                  <p className="text-sm text-gray-600 mb-3">
                    Due: {new Date(assignment.due_date).toLocaleDateString()}
                  </p>
                )}

                {assignment.status === 'Not Started' && (
                  <button
                    onClick={() => handleStartCourse(assignment.id)}
                    className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                  >
                    Start Course
                  </button>
                )}

                {assignment.status === 'In Progress' && (
                  <div className="space-y-2">
                    {assignment.course_external_url ? (
                      <a
                        href={assignment.course_external_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium text-center"
                      >
                        Continue Learning
                      </a>
                    ) : (
                      <div className="w-full px-4 py-2 bg-gray-400 text-white rounded-lg text-center font-medium cursor-not-allowed">
                        No URL Available
                      </div>
                    )}
                    <button
                      onClick={() => setSelectedAssignment(assignment)}
                      className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
                    >
                      Mark Complete
                    </button>
                  </div>
                )}

                {assignment.status === 'Completed' && (
                  <div className="space-y-2">
                    <p className="text-sm text-green-600 font-medium">
                      ✓ Completed on {assignment.completed_at ? new Date(assignment.completed_at).toLocaleDateString() : 'N/A'}
                    </p>
                    {assignment.certificate_url && (
                      <a
                        href={assignment.certificate_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:underline"
                      >
                        View Certificate
                      </a>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Complete Course Modal */}
      {selectedAssignment && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold mb-4">Complete Course</h2>
            <p className="text-gray-600 mb-4">{selectedAssignment.course_title}</p>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Certificate (Optional)
                </label>
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => setCertificateFile(e.target.files?.[0] || null)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notes (Optional)
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="Add any notes about the course..."
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleCompleteCourse}
                  disabled={uploading}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  {uploading ? 'Submitting...' : 'Submit'}
                </button>
                <button
                  onClick={() => {
                    setSelectedAssignment(null);
                    setCertificateFile(null);
                    setNotes('');
                  }}
                  className="flex-1 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
