# Learning Auto-Assignment Feature

## Overview

This feature automatically assigns learning courses to employees based on their skill gaps. When an employee's skill level is below the required level for their band, all courses mapped to that skill are automatically assigned as mandatory learning.

## How It Works

### 1. Skill-Course Mapping
- Each course can be mapped to a specific skill during creation
- This mapping enables the system to identify which courses are relevant for skill development
- Courses without skill mapping won't be auto-assigned

### 2. Role Requirements (Band-Based)
- Each band (A, B, C, L1, L2) has defined skill requirements
- Requirements specify the minimum skill level needed for each skill
- Example: Band B might require "Intermediate" level in Python

### 3. Skill Gap Detection
- The system compares each employee's current skill level with their band's requirements
- If current level < required level, a skill gap is identified
- Skill levels: Beginner (1) < Developing (2) < Intermediate (3) < Advanced (4) < Expert (5)

### 4. Automatic Assignment
- When a skill gap is detected, all courses mapped to that skill are assigned to the employee
- Assignments are created with "Not Started" status
- Duplicate assignments are automatically skipped

## Setup Instructions

### Step 1: Apply Database Migration

Run the migration to create the role_requirements table:

```bash
cd backend
python migrations/apply_role_requirements.py
```

### Step 2: Define Role Requirements

You can add role requirements via:

**Option A: Direct Database Insert**
```sql
-- Example: Python requirements for different bands
INSERT INTO role_requirements (band, skill_id, required_rating, is_required)
SELECT 'A', id, 'Beginner', TRUE FROM skills WHERE name = 'Python';

INSERT INTO role_requirements (band, skill_id, required_rating, is_required)
SELECT 'B', id, 'Intermediate', TRUE FROM skills WHERE name = 'Python';

INSERT INTO role_requirements (band, skill_id, required_rating, is_required)
SELECT 'C', id, 'Advanced', TRUE FROM skills WHERE name = 'Python';
```

**Option B: API Endpoint**
```bash
POST /api/role-requirements
{
  "band": "B",
  "skill_id": 1,
  "required_rating": "Intermediate",
  "is_required": true
}
```

### Step 3: Create Courses with Skill Mapping

When creating courses in the admin panel:
1. Go to Learning Management → Courses
2. Click "Create Course"
3. Fill in course details
4. **Important**: Select a skill from the "Map to Skill" dropdown
5. This mapping enables auto-assignment for that skill

### Step 4: Trigger Auto-Assignment

**Option A: Auto-Assign All Employees**
1. Go to Learning Management → Auto-Assign by Skill Gap
2. Click "🚀 Auto-Assign All Employees"
3. Review the results showing assignments made

**Option B: Auto-Assign Individual Employee**
1. Go to Learning Management → Auto-Assign by Skill Gap
2. Find the employee in the skill gap report
3. Click "Auto-Assign" button next to their name

**Option C: API Endpoint**
```bash
# Auto-assign all employees
POST /api/learning/auto-assign-by-skill-gap

# Auto-assign specific employee
POST /api/learning/auto-assign-for-employee/{employee_id}
```

## API Endpoints

### Learning Auto-Assignment

- `POST /api/learning/auto-assign-by-skill-gap` - Auto-assign courses to all employees based on skill gaps
- `POST /api/learning/auto-assign-for-employee/{employee_id}` - Auto-assign courses to specific employee
- `GET /api/learning/skill-gap-report` - Get detailed report of all skill gaps and available courses

### Role Requirements Management

- `POST /api/role-requirements` - Create new role requirement
- `GET /api/role-requirements` - Get all role requirements (with optional filters)
- `PUT /api/role-requirements/{id}` - Update role requirement
- `DELETE /api/role-requirements/{id}` - Delete role requirement

## Example Workflow

1. **Admin sets up role requirements:**
   - Band A: Python (Beginner), JavaScript (Beginner)
   - Band B: Python (Intermediate), JavaScript (Intermediate)
   - Band C: Python (Advanced), JavaScript (Advanced)

2. **Admin creates courses with skill mapping:**
   - "Python Fundamentals" → mapped to Python skill
   - "Advanced Python" → mapped to Python skill
   - "JavaScript Basics" → mapped to JavaScript skill

3. **Employee profile:**
   - Name: John Doe
   - Band: B
   - Current Skills: Python (Beginner), JavaScript (Developing)

4. **Auto-assignment triggers:**
   - Python gap detected: Current (Beginner) < Required (Intermediate)
   - Assigns: "Python Fundamentals", "Advanced Python"
   - JavaScript gap detected: Current (Developing) < Required (Intermediate)
   - Assigns: "JavaScript Basics"

5. **Employee sees mandatory learning:**
   - John logs in and sees 3 new mandatory courses
   - Can start courses, track progress, and upload certificates

## Benefits

- **Automated**: No manual tracking of skill gaps needed
- **Scalable**: Works for entire organization automatically
- **Targeted**: Only assigns relevant courses based on actual gaps
- **Transparent**: Employees see why courses are assigned (skill gap)
- **Efficient**: Prevents duplicate assignments

## Best Practices

1. **Keep role requirements updated**: Review and update requirements as roles evolve
2. **Map courses accurately**: Ensure courses are mapped to the correct skills
3. **Regular auto-assignment**: Run auto-assignment periodically (e.g., monthly)
4. **Monitor skill gap report**: Use the report to identify training needs
5. **Create multiple courses per skill**: Offer different learning paths for the same skill

## Troubleshooting

**Q: Courses aren't being auto-assigned**
- Verify role requirements exist for the employee's band
- Check that courses are mapped to skills
- Ensure employee has a band assigned
- Confirm skill gaps exist (current level < required level)

**Q: Too many courses being assigned**
- Review role requirements - they might be too strict
- Consider creating more granular skill mappings
- Use course descriptions to guide employees on which to prioritize

**Q: Duplicate assignments**
- The system automatically prevents duplicates
- If you see duplicates, check for database constraint issues

## Future Enhancements

Potential improvements for this feature:
- Due date calculation based on skill gap severity
- Priority levels for different skill gaps
- Learning path recommendations
- Progress tracking and reminders
- Integration with external learning platforms
- Skill improvement tracking after course completion
