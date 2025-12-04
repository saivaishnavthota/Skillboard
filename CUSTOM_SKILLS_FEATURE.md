# Custom Skills Feature

## Overview
This feature allows employees to add custom skills that are not available in their category template. Custom skills are displayed separately in the profile section and are fully searchable in the admin panel.

## Features

### For Employees
1. **Add Custom Skills**: Click "Add Custom Skill" button in the Edit Skills page
2. **Visual Distinction**: Custom skills are marked with a green "Custom" badge
3. **Same Functionality**: Custom skills support the same proficiency ratings as template skills
4. **Separate Display**: Custom skills appear in a dedicated section below template skills

### For Admins
- Custom skills are included in all skill searches
- Custom skills appear in employee skill reports
- Custom skills are tracked with the `is_custom` flag in the database

## Implementation Details

### Database Changes
- Added `is_custom` column to `employee_skills` table (BOOLEAN, default FALSE)
- Migration script: `backend/migrations/add_is_custom_column.sql`

### Backend Changes
1. **Models** (`backend/app/db/models.py`):
   - Added `is_custom` field to `EmployeeSkill` model

2. **Schemas** (`backend/app/schemas.py`):
   - Added `is_custom` field to `EmployeeSkillCreate`, `EmployeeSkillCreateMe`, and `EmployeeSkill` schemas

3. **CRUD** (`backend/app/db/crud.py`):
   - Updated `upsert_employee_skill` to handle `is_custom` parameter

4. **API** (`backend/app/api/userskills.py`):
   - Modified `/api/user-skills/me` endpoint to automatically mark skills as custom if they're not in the employee's category template
   - Skills added with `is_custom=true` bypass template validation

### Frontend Changes
1. **OnboardingMapSkills** (`frontend/src/pages/OnboardingMapSkills.tsx`):
   - Added "Add Custom Skill" button with input field
   - Custom skills are visually distinguished with green styling
   - Separate section for custom skills in the skills list

2. **EmployeeDashboard** (`frontend/src/pages/EmployeeDashboard.tsx`):
   - Custom skills displayed in a separate section below template skills
   - Green badge and styling to identify custom skills

3. **API Types** (`frontend/src/services/api.ts`):
   - Added `is_custom` field to `EmployeeSkill` interface
   - Updated `createMySkill` to accept `is_custom` parameter

4. **SkillCard** (`frontend/src/components/SkillCard.tsx`):
   - Added `is_custom` field to `SkillCardData` interface

## Usage

### Adding a Custom Skill
1. Navigate to Edit Skills page (click "Edit Skills" button on dashboard)
2. Click "Add Custom Skill" button in the left panel
3. Enter the skill name
4. Click "Add" or press Enter
5. Set the proficiency level using the rating buttons (B/D/I/A/E)

### Viewing Custom Skills
- On the profile page, custom skills appear in a separate "Custom Skills" section
- Each custom skill has a green "Custom" badge
- Custom skills have the same proficiency indicators as template skills

## Technical Notes

### Validation Logic
- When a skill is added via the API, the system checks if it exists in the employee's category template
- If the skill is not in the template, it's automatically marked as `is_custom=true`
- Custom skills bypass template validation

### Search and Reporting
- Custom skills are included in all admin searches
- The `is_custom` flag can be used to filter or identify user-added skills
- Custom skills appear in skill gap analysis and band calculations

## Migration

To apply the database migration:

```bash
# Using Docker (recommended)
cat backend/migrations/add_is_custom_column.sql | docker exec -i skillboard-postgres psql -U skillboard -d skillboard

# Or using Python script (requires database connection)
cd backend
python3 migrations/add_is_custom_to_employee_skills.py
```

## Future Enhancements
- Admin approval workflow for custom skills
- Suggest similar existing skills when adding custom skills
- Bulk import of custom skills
- Analytics on most commonly added custom skills
