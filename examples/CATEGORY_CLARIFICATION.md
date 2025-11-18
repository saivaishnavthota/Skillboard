# Category System - Important Clarification

## Two Different Types of Categories

The application uses **TWO completely different types of categories**:

### 1. Employee Category (Department/Role Category)
- **What**: The department or role category an employee belongs to
- **Examples**: "Technical", "HR", "Sales", "Finance", "Marketing"
- **Purpose**: Controls which skills an employee can see and add
- **Where**: Set in employee import Excel (`category` column)
- **Used in**: Category templates to link skills to employee categories

### 2. Skill Category (Skill Grouping/Tag)
- **What**: A grouping of 4-5 related skills for organization
- **Examples**: "Programming", "Database", "Cloud", "DevOps", "SAP"
- **Purpose**: Just for organizing and grouping skills in the master list
- **Where**: Optional column in skill import Excel (`skill_category` column)
- **Used in**: Skill master list organization only

## How They Work Together

### Example Scenario:

**Employee Import:**
```
employee_id | name      | category
E001        | John Doe  | Technical
E002        | Jane Smith| HR
```

**Skill Import (Master Skills):**
```
name      | description        | skill_category
React     | React framework    | Programming
Python    | Python language    | Programming
SQL       | SQL database       | Database
Recruitment| Hiring process     | HR Tools
```

**Category Template Import:**
- Upload `technical_skills.xlsx` with `category=Technical` (form parameter)
  - This assigns React, Python, SQL to the "Technical" employee category
- Upload `hr_skills.xlsx` with `category=HR` (form parameter)
  - This assigns Recruitment to the "HR" employee category

**Result:**
- John (Technical employee) sees: React, Python, SQL
- Jane (HR employee) sees: Recruitment
- The `skill_category` (Programming, Database, HR Tools) is just for organization

## Excel Format Clarification

### When Importing Category Templates:

**Form Parameter (Required):**
- `category` = Employee category (Technical, HR, Sales, etc.)

**Excel Columns:**
- `name` = Skill name (required)
- `description` = Skill description (optional)
- `skill_category` = Skill grouping like "Programming", "Database" (optional, just for organization)

**Example Excel File: `technical_skills.xlsx`**
```
name      | description        | skill_category
React     | React framework    | Programming
Python    | Python language    | Programming
SQL       | SQL database       | Database
```

**Upload Command:**
```bash
curl -X POST "http://localhost:8000/api/admin/import-category-templates" \
  -F "file=@technical_skills.xlsx" \
  -F "category=Technical"  # ← This is the EMPLOYEE category
```

## Key Points

1. **Employee Category** (form parameter) = Which employees can see these skills
2. **Skill Category** (Excel column) = Just for organizing skills (optional)
3. They are **completely independent** - a skill can have `skill_category="Programming"` but be assigned to multiple employee categories (Technical, IT, etc.)
4. The `skill_category` column is optional - you can leave it blank if you don't need skill grouping

