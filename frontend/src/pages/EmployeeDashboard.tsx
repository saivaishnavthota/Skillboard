/** Employee Dashboard - Main page for employees to manage their skills. */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { DndContext, useSensor, useSensors, PointerSensor, KeyboardSensor, closestCenter, DragEndEvent } from '@dnd-kit/core';
import { arrayMove } from '@dnd-kit/sortable';
import { SkillBrowser } from '../components/SkillBrowser';
import { ColumnsArea } from '../components/ColumnsArea';
import { SkillCardData } from '../components/SkillCard';
import { authApi, userSkillsApi, skillsApi, Skill, EmployeeSkill } from '../services/api';

const DndContextWrapper: React.FC<{ 
  children: React.ReactNode;
  onDragEnd: (event: DragEndEvent) => void;
}> = ({ children, onDragEnd }) => {
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor)
  );

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={onDragEnd}>
      {children}
    </DndContext>
  );
};

export const EmployeeDashboard: React.FC = () => {
  const [existingSkills, setExistingSkills] = useState<SkillCardData[]>([]);
  const [interestedSkills, setInterestedSkills] = useState<SkillCardData[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');
  const [user, setUser] = useState(authApi.getUser());
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is logged in
    if (!user) {
      navigate('/login');
      return;
    }

    loadSkills();
  }, []);

  const loadSkills = async () => {
    try {
      setLoading(true);
      const employeeSkills = await userSkillsApi.getMySkills();
      
      // Separate existing and interested skills
      const existing: SkillCardData[] = [];
      const interested: SkillCardData[] = [];
      
      employeeSkills.forEach((es: EmployeeSkill) => {
        const skillData: SkillCardData = {
          id: es.skill_id,
          name: es.skill?.name || 'Unknown',
          description: es.skill?.description,
          rating: es.rating || undefined,  // Rating may be null for interested skills
          years_experience: es.years_experience,
        };
        
        if (es.is_interested) {
          interested.push(skillData);
        } else {
          existing.push(skillData);
        }
      });
      
      setExistingSkills(existing);
      setInterestedSkills(interested);
    } catch (error) {
      console.error('Failed to load skills:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveSkills = async () => {
    setSaving(true);
    setSaveMessage('');
    
    try {
      // Save all existing skills
      for (const skill of existingSkills) {
        await userSkillsApi.createMySkill({
          skill_name: skill.name,
          rating: skill.rating || 'Beginner',  // Required for existing skills
          years_experience: skill.years_experience,
          is_interested: false,
        });
      }
      
      // Save all interested skills (no rating needed)
      for (const skill of interestedSkills) {
        await userSkillsApi.createMySkill({
          skill_name: skill.name,
          rating: undefined,  // No rating for interested skills
          years_experience: skill.years_experience,
          is_interested: true,
        });
      }
      
      setSaveMessage('Skills saved successfully!');
      setTimeout(() => setSaveMessage(''), 3000);
    } catch (error) {
      console.error('Failed to save skills:', error);
      setSaveMessage('Failed to save skills. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleSkillAdd = (
    skill: SkillCardData,
    column: 'existing' | 'interested'
  ) => {
    // Check if skill already exists
    const existsInExisting = existingSkills.some((s) => s.id === skill.id);
    const existsInInterested = interestedSkills.some((s) => s.id === skill.id);

    if (existsInExisting || existsInInterested) {
      return;
    }

    if (column === 'existing') {
      setExistingSkills([...existingSkills, skill]);
    } else {
      setInterestedSkills([...interestedSkills, skill]);
    }
  };

  const handleRatingChange = (
    skillId: number,
    rating: 'Beginner' | 'Developing' | 'Intermediate' | 'Advanced' | 'Expert'
  ) => {
    setExistingSkills(
      existingSkills.map((s) => (s.id === skillId ? { ...s, rating } : s))
    );
    setInterestedSkills(
      interestedSkills.map((s) => (s.id === skillId ? { ...s, rating } : s))
    );
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (!over) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    // Check if dragging from master list
    if (activeId.toString().startsWith('skill-')) {
      const skillId = parseInt(activeId.toString().replace('skill-', ''));
      const skillData = active.data.current?.skill as Skill;
      
      if (skillData) {
        if (overId === 'existing-column' || overId.toString().startsWith('existing-')) {
          handleSkillAdd(
            {
              id: skillData.id,
              name: skillData.name,
              description: skillData.description,
              rating: 'Beginner',
            },
            'existing'
          );
        } else if (overId === 'interested-column' || overId.toString().startsWith('interested-')) {
          handleSkillAdd(
            {
              id: skillData.id,
              name: skillData.name,
              description: skillData.description,
              rating: undefined,  // No rating for interested skills
            },
            'interested'
          );
        }
      }
      return;
    }

    // Handle moving between columns
    const activeSkillId = parseInt(activeId.toString());
    const activeInExisting = existingSkills.find((s) => s.id === activeSkillId);
    const activeInInterested = interestedSkills.find((s) => s.id === activeSkillId);

    if (activeInExisting) {
      if (overId === 'interested-column' || overId.toString().startsWith('interested-')) {
        // Move from existing to interested - remove rating
        setExistingSkills(existingSkills.filter((s) => s.id !== activeSkillId));
        setInterestedSkills([...interestedSkills, { ...activeInExisting, rating: undefined }]);
      } else {
        // Reorder within existing
        const overSkillId = parseInt(overId.toString());
        const overInExisting = existingSkills.find((s) => s.id === overSkillId);
        if (overInExisting) {
          const oldIndex = existingSkills.findIndex((s) => s.id === activeSkillId);
          const newIndex = existingSkills.findIndex((s) => s.id === overSkillId);
          setExistingSkills(arrayMove(existingSkills, oldIndex, newIndex));
        }
      }
    } else if (activeInInterested) {
      if (overId === 'existing-column' || overId.toString().startsWith('existing-')) {
        // Move from interested to existing - add default rating
        setInterestedSkills(interestedSkills.filter((s) => s.id !== activeSkillId));
        setExistingSkills([...existingSkills, { ...activeInInterested, rating: 'Beginner' }]);
      } else {
        // Reorder within interested
        const overSkillId = parseInt(overId.toString());
        const overInInterested = interestedSkills.find((s) => s.id === overSkillId);
        if (overInInterested) {
          const oldIndex = interestedSkills.findIndex((s) => s.id === activeSkillId);
          const newIndex = interestedSkills.findIndex((s) => s.id === overSkillId);
          setInterestedSkills(arrayMove(interestedSkills, oldIndex, newIndex));
        }
      }
    }
  };

  const handleLogout = () => {
    authApi.logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl text-gray-600">Loading your skills...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">Skillboard - My Skills</h1>
          <div className="flex gap-2 items-center">
            <span className="text-sm text-gray-600">{user?.email}</span>
            <button
              onClick={() => navigate('/skill-gap')}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Skill Gap Analysis
            </button>
            {user?.is_admin && (
              <button
                onClick={() => navigate('/admin/dashboard')}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                Admin Dashboard
              </button>
            )}
            <button
              onClick={saveSkills}
              disabled={saving}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
            {saveMessage && (
              <span className={`text-sm ${saveMessage.includes('Failed') ? 'text-red-600' : 'text-green-600'}`}>
                {saveMessage}
              </span>
            )}
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <DndContextWrapper onDragEnd={handleDragEnd}>
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="grid grid-cols-4 gap-4 h-[calc(100vh-120px)]">
            {/* Left Panel: Master Skills */}
            <div className="col-span-1 bg-white rounded-lg shadow-md border border-gray-200">
              <div className="p-4 border-b border-gray-200">
                <input
                  type="text"
                  placeholder="Search skills..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <SkillBrowser 
                searchQuery={searchQuery} 
                excludeSkillIds={[
                  ...existingSkills.map(s => s.id),
                  ...interestedSkills.map(s => s.id)
                ]}
              />
            </div>

            {/* Right Area: Two Columns */}
            <div className="col-span-3">
              <ColumnsArea
                existingSkills={existingSkills}
                interestedSkills={interestedSkills}
                onExistingSkillsChange={setExistingSkills}
                onInterestedSkillsChange={setInterestedSkills}
                onRatingChange={handleRatingChange}
                onSkillAdd={handleSkillAdd}
              />
            </div>
          </div>
        </div>
      </DndContextWrapper>
    </div>
  );
};

