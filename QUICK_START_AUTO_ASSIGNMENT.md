# Quick Start: Learning Auto-Assignment

Get the learning auto-assignment feature up and running in 5 minutes!

## Prerequisites

- Backend server running
- Admin access to the system
- At least one employee with a band assigned
- At least one skill in the system

## Step 1: Apply Database Migration (30 seconds)

```bash
cd backend
python3 migrations/apply_role_requirements.py
```

Expected output:
```
Applying role requirements migration...
✓ Role requirements migration applied successfully!
```

## Step 2: Add Role Requirements (2 minutes)

Choose one method:

### Method A: Using Database (Fastest)

Connect to your PostgreSQL database and run:

```sql
-- Example: Set Python requirements for all bands
INSERT INTO role_requirements (band, skill_id, required_rating, is_required)
SELECT 'A', id, 'Beginner', TRUE FROM skills WHERE name = 'Python' LIMIT 1;

INSERT INTO role_requirements (band, skill_id, required_rating, is_required)
SELECT 'B', id, 'Intermediate', TRUE FROM skills WHERE name = 'Python' LIMIT 1;

INSERT INTO role_requirements (band, skill_id, required_rating, is_required)
SELECT 'C', id, 'Advanced', TRUE FROM skills WHERE name = 'Python' LIMIT 1;

INSERT INTO role_requirements (band, skill_id, required_rating, is_required)
SELECT 'L1', id, 'Advanced', TRUE FROM skills WHERE name = 'Python' LIMIT 1;

INSERT INTO role_requirements (band, skill_id, required_rating, is_required)
SELECT 'L2', id, 'Expert', TRUE FROM skills WHERE name = 'Python' LIMIT 1;
```

### Method B: Using API

```bash
# Get your auth token first
TOKEN="your_admin_token_here"

# Add requirement for Band B - Python - Intermediate
curl -X POST http://localhost:8000/api/role-requirements \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "band": "B",
    "skill_id": 1,
    "required_rating": "Intermediate",
    "is_required": true
  }'
```

## Step 3: Create Courses with Skill Mapping (1 minute)

1. Log in as admin
2. Go to **Learning Management** → **Courses** tab
3. Click **"+ Create Course"**
4. Fill in:
   - **Title**: "Python Fundamentals"
   - **Description**: "Learn Python basics"
   - **Map to Skill**: Select "Python" from dropdown ⚠️ **IMPORTANT**
   - **External URL**: https://your-learning-platform.com/python
   - **Mandatory**: Check if desired
5. Click **"Create"**

Repeat for other skills as needed.

## Step 4: Test the Feature (1 minute)

### Option A: Run Test Script

```bash
cd backend
python3 test_auto_assignment.py
```

This will show:
- Employees and their bands
- Available skills and courses
- Role requirements
- Detected skill gaps
- Available courses for each gap

### Option B: Use Admin UI

1. Go to **Learning Management** → **Auto-Assign by Skill Gap** tab
2. You'll see a report of all employees with skill gaps
3. Click **"🚀 Auto-Assign All Employees"** to assign courses automatically

## Step 5: Verify Assignments (30 seconds)

1. Go to **Learning Management** → **Assignments** tab
2. You should see new assignments created
3. Log in as an employee to see their mandatory learning courses

## Troubleshooting

### No skill gaps detected?

**Check:**
- Do employees have bands assigned?
- Do role requirements exist for those bands?
- Are employee skill levels below required levels?

```sql
-- Check employee bands
SELECT employee_id, name, band FROM employees LIMIT 10;

-- Check role requirements
SELECT * FROM role_requirements;

-- Check employee skills
SELECT e.name, s.name as skill, es.rating 
FROM employee_skills es
JOIN employees e ON e.id = es.employee_id
JOIN skills s ON s.id = es.skill_id
LIMIT 10;
```

### Courses not being assigned?

**Check:**
- Are courses mapped to skills? (skill_id should not be NULL)
- Do role requirements exist for the skill?
- Is there actually a skill gap?

```sql
-- Check course-skill mappings
SELECT c.title, s.name as skill_name 
FROM courses c
LEFT JOIN skills s ON s.id = c.skill_id;
```

### "No courses available for this skill"?

**Solution:**
- Create a course and map it to that skill
- Or remove the role requirement if the skill isn't critical

## Example Complete Workflow

```bash
# 1. Apply migration
cd backend
python3 migrations/apply_role_requirements.py

# 2. Add requirements (using psql)
psql -U your_user -d skillboard -c "
INSERT INTO role_requirements (band, skill_id, required_rating, is_required)
SELECT 'B', id, 'Intermediate', TRUE FROM skills WHERE name = 'Python' LIMIT 1;
"

# 3. Test
python3 test_auto_assignment.py

# 4. Use admin UI to create courses and trigger auto-assignment
```

## Next Steps

Once the basic setup is working:

1. **Add more role requirements** for all your bands and critical skills
2. **Create comprehensive course library** mapped to skills
3. **Set up regular auto-assignment** (weekly/monthly)
4. **Monitor the skill gap report** to identify training needs
5. **Track course completion** to measure skill improvement

## Quick Reference

### Key URLs
- Admin Learning: `http://localhost:5173/admin/learning`
- Employee Learning: `http://localhost:5173/learning`

### Key API Endpoints
- Auto-assign all: `POST /api/learning/auto-assign-by-skill-gap`
- Skill gap report: `GET /api/learning/skill-gap-report`
- Role requirements: `GET /api/role-requirements`

### Skill Rating Levels
1. Beginner
2. Developing
3. Intermediate
4. Advanced
5. Expert

### Common Bands
- A: Entry level
- B: Mid level
- C: Senior level
- L1: Leadership level 1
- L2: Leadership level 2

## Support

For detailed documentation, see:
- `LEARNING_AUTO_ASSIGNMENT.md` - Complete feature documentation
- `IMPLEMENTATION_SUMMARY.md` - Technical implementation details

For issues or questions, check the troubleshooting section above or review the test script output.
