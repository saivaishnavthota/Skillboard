/** Admin Learning Management - Create courses and assign to employees. */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi, learningApi, adminDashboardApi, skillsApi, Course, CourseAssignment, Employee, Skill } from '../services/api';
import NxzenLogo from '../images/Nxzen.jpg';

export const AdminLearning: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'courses' | 'assignments' | 'auto-assign'>('courses');
  const [courses, setCourses] = useState<Course[]>([]);
  const [assignments, setAssignments] = useState<CourseAssignment[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateCourse, setShowCreateCourse] = useState(false);
  const [showAssignCourse, setShowAssignCourse] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [selectedEmployees, setSelectedEmployees] = useState<number[]>([]);
  const [skillGapReport, setSkillGapReport] = useState<any[]>([]);
  const [autoAssigning, setAutoAssigning] = useState(false);
  const [autoAssignResult, setAutoAssignResult] = useState<any>(null);
  
  // Form states
  const [courseTitle, setCourseTitle] = useState('');
  const [courseDescription, setCourseDescription] = useState('');
  const [courseUrl, setCourseUrl] = useState('');
  const [courseSkillId, setCourseSkillId] = useState<number | undefined>(undefined);
  const [isMandatory, setIsMandatory] = useState(false);
  const [dueDate, setDueDate] = useState('');
  const [skills, setSkills] = useState<any[]>([]);
  
  const navigate = useNavigate();
  const user = authApi.getUser();

  useEffect(() => {
    if (!user?.is_admin) {
      navigate('/login');
      return;
    }
    loadData();
    loadSkills();
  }, [activeTab]);

  const loadData = async () => {
    try {
      setLoading(true);
      if (activeTab === 'courses') {
        const coursesData = await learningApi.getAllCourses();
        setCourses(coursesData);
      } else if (activeTab === 'assignments') {
        const assignmentsData = await learningApi.getAllAssignments();
        setAssignments(assignmentsData);
      } else if (activeTab === 'auto-assign') {
        const reportData = await learningApi.getSkillGapReport();
        setSkillGapReport(reportData);
      }
      
      // Load employees for assignment
      const employeesData = await adminDashboardApi.getEmployees(0, 1000);
      setEmployees(employeesData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSkills = async () => {
    try {
      // Try the simple /all endpoint first, fallback to regular endpoint
      let skillsData: Skill[] = [];
      try {
        skillsData = await skillsApi.getAllSimple(1000);
      } catch (e) {
        console.log('Falling back to regular skills endpoint');
        skillsData = await skillsApi.getAll();
      }
      console.log('Loaded skills:', skillsData.length);
      setSkills(skillsData);
    } catch (error) {
      console.error('Failed to load skills:', error);
      setSkills([]);
    }
  };

  const handleCreateCourse = async () => {
    if (!courseTitle.trim()) return;

    try {
      await learningApi.createCourse({
        title: courseTitle,
        description: courseDescription || undefined,
        skill_id: courseSkillId,
        external_url: courseUrl || undefined,
        is_mandatory: isMandatory,
      });
      
      setShowCreateCourse(false);
      setCourseTitle('');
      setCourseDescription('');
      setCourseUrl('');
      setCourseSkillId(undefined);
      setIsMandatory(false);
      loadData();
    } catch (error) {
      console.error('Failed to create course:', error);
    }
  };

  const handleAutoAssignAll = async () => {
    if (!confirm('This will automatically assign courses to all employees based on their skill gaps. Continue?')) return;

    try {
      setAutoAssigning(true);
      const result = await learningApi.autoAssignBySkillGap();
      setAutoAssignResult(result);
      loadData();
    } catch (error) {
      console.error('Failed to auto-assign courses:', error);
      alert('Failed to auto-assign courses. Please try again.');
    } finally {
      setAutoAssigning(false);
    }
  };

  const handleAutoAssignEmployee = async (employeeId: number) => {
    try {
      const result = await learningApi.autoAssignForEmployee(employeeId);
      alert(`Successfully assigned ${result.assigned} courses to employee`);
      loadData();
    } catch (error) {
      console.error('Failed to auto-assign courses:', error);
      alert('Failed to auto-assign courses. Please try again.');
    }
  };

  const handleAssignCourse = async () => {
    if (!selectedCourse || selectedEmployees.length === 0) return;

    try {
      await learningApi.assignCourse({
        course_id: selectedCourse.id,
        employee_ids: selectedEmployees,
        due_date: dueDate || undefined,
      });
      
      setShowAssignCourse(false);
      setSelectedCourse(null);
      setSelectedEmployees([]);
      setDueDate('');
      loadData();
    } catch (error) {
      console.error('Failed to assign course:', error);
    }
  };

  const handleDeleteCourse = async (courseId: number) => {
    if (!confirm('Are you sure you want to delete this course?')) return;

    try {
      await learningApi.deleteCourse(courseId);
      loadData();
    } catch (error) {
      console.error('Failed to delete course:', error);
    }
  };

  const toggleEmployeeSelection = (employeeId: number) => {
    setSelectedEmployees(prev =>
      prev.includes(employeeId)
        ? prev.filter(id => id !== employeeId)
        : [...prev, employeeId]
    );
  };

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

  return (
    <div className="min-h-screen bg-[#F6F2F4]">
      <header className="bg-[#F6F2F4] shadow-sm border-b border-gray-200">
        <div className="w-full px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <img src={NxzenLogo} alt="Nxzen" className="h-8 w-8 object-cover" />
            <span className="text-xl font-semibold text-gray-800">nxzen</span>
            <span aria-hidden className="h-6 w-px bg-gray-300" />
            <h1 className="text-2xl font-bold text-gray-800 italic">Learning Management</h1>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate('/admin/dashboard')}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              Back to Dashboard
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
        {/* Tabs */}
        <div className="mb-6 flex gap-3">
          <button
            onClick={() => setActiveTab('courses')}
            className={`px-6 py-3 rounded-lg font-semibold ${
              activeTab === 'courses' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 border border-gray-300'
            }`}
          >
            Courses ({courses.length})
          </button>
          <button
            onClick={() => setActiveTab('assignments')}
            className={`px-6 py-3 rounded-lg font-semibold ${
              activeTab === 'assignments' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 border border-gray-300'
            }`}
          >
            Assignments ({assignments.length})
          </button>
          <button
            onClick={() => setActiveTab('auto-assign')}
            className={`px-6 py-3 rounded-lg font-semibold ${
              activeTab === 'auto-assign' ? 'bg-purple-600 text-white' : 'bg-white text-gray-700 border border-gray-300'
            }`}
          >
            Auto-Assign by Skill Gap
          </button>
        </div>

        {/* Courses Tab */}
        {activeTab === 'courses' && (
          <div>
            <div className="mb-6 flex justify-end">
              <button
                onClick={() => setShowCreateCourse(true)}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
              >
                + Create Course
              </button>
            </div>

            {loading ? (
              <div className="text-center py-12 text-gray-500">Loading courses...</div>
            ) : courses.length === 0 ? (
              <div className="text-center py-12 text-gray-500 bg-white rounded-lg">
                No courses created yet. Click "Create Course" to add one.
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Skill</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Mandatory</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {courses.map((course) => (
                      <tr key={course.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div className="text-sm font-medium text-gray-900">{course.title}</div>
                          {course.external_url && (
                            <a
                              href={course.external_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-blue-600 hover:underline"
                            >
                              View Course
                            </a>
                          )}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-700">
                          {course.skill_name ? (
                            <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                              {course.skill_name}
                            </span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">{course.description || '-'}</td>
                        <td className="px-6 py-4 text-center">
                          {course.is_mandatory ? (
                            <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">
                              Mandatory
                            </span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-center">
                          <div className="flex items-center justify-center gap-2">
                            <button
                              onClick={() => {
                                setSelectedCourse(course);
                                setShowAssignCourse(true);
                              }}
                              className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                            >
                              Assign
                            </button>
                            <button
                              onClick={() => handleDeleteCourse(course.id)}
                              className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Assignments Tab */}
        {activeTab === 'assignments' && (
          <div>
            {loading ? (
              <div className="text-center py-12 text-gray-500">Loading assignments...</div>
            ) : assignments.length === 0 ? (
              <div className="text-center py-12 text-gray-500 bg-white rounded-lg">
                No assignments yet. Assign courses to employees from the Courses tab.
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Course</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Due Date</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Completed</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {assignments.map((assignment) => (
                      <tr key={assignment.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm font-medium text-gray-900">{assignment.employee_name}</td>
                        <td className="px-6 py-4 text-sm text-gray-900">{assignment.course_title}</td>
                        <td className="px-6 py-4 text-center">
                          <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(assignment.status)}`}>
                            {assignment.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center text-sm text-gray-500">
                          {assignment.due_date ? new Date(assignment.due_date).toLocaleDateString() : '-'}
                        </td>
                        <td className="px-6 py-4 text-center text-sm text-gray-500">
                          {assignment.completed_at ? new Date(assignment.completed_at).toLocaleDateString() : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Auto-Assign Tab */}
        {activeTab === 'auto-assign' && (
          <div>
            <div className="mb-6 bg-blue-50 border-l-4 border-blue-400 p-4">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-blue-700">
                    This feature automatically assigns courses to employees based on their skill gaps. 
                    Courses mapped to skills will be assigned to employees whose current skill level is below their band's required level.
                  </p>
                </div>
              </div>
            </div>

            <div className="mb-6 flex justify-end">
              <button
                onClick={handleAutoAssignAll}
                disabled={autoAssigning}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-semibold disabled:opacity-50"
              >
                {autoAssigning ? 'Processing...' : '🚀 Auto-Assign All Employees'}
              </button>
            </div>

            {autoAssignResult && (
              <div className="mb-6 bg-green-50 border-l-4 border-green-400 p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-green-700">
                      <strong>{autoAssignResult.message}</strong>
                    </p>
                    <p className="text-xs text-green-600 mt-1">
                      Assigned: {autoAssignResult.assigned} | Skipped: {autoAssignResult.skipped}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {loading ? (
              <div className="text-center py-12 text-gray-500">Loading skill gap report...</div>
            ) : skillGapReport.length === 0 ? (
              <div className="text-center py-12 text-gray-500 bg-white rounded-lg">
                No skill gaps found. All employees meet their band requirements!
              </div>
            ) : (
              <div className="space-y-6">
                {skillGapReport.map((employee) => (
                  <div key={employee.employee_id} className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-bold text-gray-900">{employee.employee_name}</h3>
                        <p className="text-sm text-gray-500">Band: {employee.band}</p>
                      </div>
                      <button
                        onClick={() => handleAutoAssignEmployee(employee.employee_id)}
                        className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium"
                      >
                        Auto-Assign
                      </button>
                    </div>

                    <div className="space-y-4">
                      {employee.skill_gaps.map((gap: any) => (
                        <div key={gap.skill_id} className="border-l-4 border-orange-400 pl-4 py-2">
                          <div className="flex items-center justify-between mb-2">
                            <div>
                              <span className="font-semibold text-gray-900">{gap.skill_name}</span>
                              <span className="ml-3 text-sm text-gray-600">
                                Current: <span className="text-orange-600 font-medium">{gap.current_level}</span>
                                {' → '}
                                Required: <span className="text-green-600 font-medium">{gap.required_level}</span>
                              </span>
                            </div>
                          </div>

                          {gap.assigned_courses.length > 0 && (
                            <div className="mt-2">
                              <p className="text-xs text-gray-500 mb-1">Assigned Courses:</p>
                              <div className="flex flex-wrap gap-2">
                                {gap.assigned_courses.map((course: any) => (
                                  <span key={course.course_id} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                                    {course.course_title} ({course.status})
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {gap.available_courses.length > 0 && (
                            <div className="mt-2">
                              <p className="text-xs text-gray-500 mb-1">Available Courses:</p>
                              <div className="flex flex-wrap gap-2">
                                {gap.available_courses.map((course: any) => (
                                  <span key={course.course_id} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                                    {course.course_title}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {gap.assigned_courses.length === 0 && gap.available_courses.length === 0 && (
                            <p className="text-xs text-red-600 mt-2">⚠️ No courses available for this skill</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Create Course Modal */}
      {showCreateCourse && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold mb-4">Create New Course</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Course Title *</label>
                <input
                  type="text"
                  value={courseTitle}
                  onChange={(e) => setCourseTitle(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="e.g., AWS Certification"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  value={courseDescription}
                  onChange={(e) => setCourseDescription(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="Course description..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Map to Skill (for auto-assignment)</label>
                <select
                  value={courseSkillId || ''}
                  onChange={(e) => setCourseSkillId(e.target.value ? Number(e.target.value) : undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="">-- No Skill Mapping --</option>
                  {skills.map((skill) => (
                    <option key={skill.id} value={skill.id}>
                      {skill.name} {skill.category ? `(${skill.category})` : ''}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  Mapping a course to a skill enables automatic assignment based on skill gaps
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">External Learning Platform URL</label>
                <input
                  type="url"
                  value={courseUrl}
                  onChange={(e) => setCourseUrl(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="https://learning-platform.com/course"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="mandatory"
                  checked={isMandatory}
                  onChange={(e) => setIsMandatory(e.target.checked)}
                  className="w-4 h-4 text-red-600 rounded"
                />
                <label htmlFor="mandatory" className="text-sm font-medium text-gray-700">
                  Mark as Mandatory
                </label>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleCreateCourse}
                  disabled={!courseTitle.trim()}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  Create
                </button>
                <button
                  onClick={() => {
                    setShowCreateCourse(false);
                    setCourseTitle('');
                    setCourseDescription('');
                    setCourseUrl('');
                    setCourseSkillId(undefined);
                    setIsMandatory(false);
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

      {/* Assign Course Modal */}
      {showAssignCourse && selectedCourse && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">Assign Course: {selectedCourse.title}</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Due Date (Optional)</label>
                <input
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Employees ({selectedEmployees.length} selected)
                </label>
                <div className="border border-gray-300 rounded-lg max-h-64 overflow-y-auto">
                  {employees.map((employee) => (
                    <div
                      key={employee.id}
                      className="flex items-center gap-2 px-3 py-2 hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                    >
                      <input
                        type="checkbox"
                        checked={selectedEmployees.includes(employee.id)}
                        onChange={() => toggleEmployeeSelection(employee.id)}
                        className="w-4 h-4 text-blue-600 rounded"
                      />
                      <span className="text-sm text-gray-900">{employee.name}</span>
                      <span className="text-xs text-gray-500">({employee.employee_id})</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleAssignCourse}
                  disabled={selectedEmployees.length === 0}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  Assign to {selectedEmployees.length} Employee{selectedEmployees.length !== 1 ? 's' : ''}
                </button>
                <button
                  onClick={() => {
                    setShowAssignCourse(false);
                    setSelectedCourse(null);
                    setSelectedEmployees([]);
                    setDueDate('');
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
