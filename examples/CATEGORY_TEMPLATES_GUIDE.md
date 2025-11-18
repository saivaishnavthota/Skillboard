# Category Skill Templates - Complete Guide

## Understanding the System

The category skill template system has **two levels of categorization**:

### 1. Employee Categories
- **What**: Categories assigned to employees (e.g., "Technical", "Sales", "HR", "Finance")
- **Where**: Stored in `employees.category` field
- **Purpose**: Determines which skills an employee can see and add

### 2. Skill Categories (Different!)
- **What**: Categories/tags for organizing skills themselves (e.g., "Programming", "SAP", "Cloud")
- **Where**: Stored in `skills.category` field
- **Purpose**: For organizing and grouping skills in the master list

**Important**: These are **separate** concepts:
- Employee categories → Control which skills employees can access
- Skill categories → Organize skills in the master list

## How Category Templates Work

### Step 1: Create Employee Categories
Assign categories to employees via Excel import:
```
employee_id | first_name | last_name | company_email | category
E001        | John       | Doe       | john@co.com   | Technical
E002        | Jane       | Smith     | jane@co.com   | Sales
```

### Step 2: Create Master Skills
Upload skills to the master list:
```
POST /api/admin/upload-skills
```
Excel format:
```
name      | description        | category
React     | React framework    | Programming
Python    | Python language    | Programming
CRM       | Customer Relations | Sales Tools
```

### Step 3: Create Category Templates
Define which skills belong to each employee category:

**Option A: Via Excel Import (Recommended for bulk upload)**
```
POST /api/admin/import-category-templates
```

Upload one Excel file per category. The category is specified as a form parameter.

**Excel Format (per file):**
```
name      | description        | category
React     | React framework    | Programming
Python    | Python language    | Programming
SQL       | SQL database        | Database
```

**Upload Process:**
1. Prepare 8 Excel files (one per category)
2. For each file, upload with category parameter:
   - File: `technical_skills.xlsx` → category="Technical"
   - File: `sales_skills.xlsx` → category="Sales"
   - etc.

**Option B: Via API (for individual skills)**
```
POST /api/categories/{category}/template
{
  "category": "Technical",
  "skill_id": 1,
  "is_required": false,
  "display_order": 1
}
```

### Step 4: Employee Experience
- Employee with category "Technical" logs in
- They see only: React, Python, SQL (from Technical template)
- They can only add skills from the Technical template
- Skills are displayed in `display_order` sequence

## Excel Import Format for Category Templates

### Required Columns
- `category` - Employee category name (must match employee categories)
- `skill_name` - Name of skill (must exist in master skills)

### Optional Columns
- `is_required` - true/false (default: false)
- `display_order` - Integer for ordering (lower = first)

### Example Excel File

| category  | skill_name  | is_required | display_order |
|-----------|-------------|-------------|---------------|
| Technical | React       | false      | 1             |
| Technical | Python      | true       | 2             |
| Technical | JavaScript  | false      | 3             |
| Technical | SQL         | false      | 4             |
| Sales     | CRM         | true       | 1             |
| Sales     | Negotiation | false      | 2             |
| Sales     | Presentation| false      | 3             |
| HR        | Recruitment | true       | 1             |
| HR        | Onboarding  | false      | 2             |

## API Endpoints Summary

### Category Management
- `GET /api/categories/` - List all categories
- `GET /api/categories/{category}/template` - Get template for category
- `POST /api/categories/{category}/template` - Add skill to template (admin)
- `DELETE /api/categories/{category}/template/{id}` - Remove skill from template (admin)

### Excel Import
- `POST /api/admin/import-category-templates` - Import templates from Excel (admin)

### Employee Management
- `POST /api/admin/import-users-excel` - Import employees with categories

## Complete Workflow Example

1. **Upload Master Skills**:
   ```
   POST /api/admin/upload-skills
   File: skills.xlsx
   Columns: name, description, category
   ```

2. **Import Employees with Categories**:
   ```
   POST /api/admin/import-users-excel
   File: employees.xlsx
   Columns: employee_id, first_name, last_name, company_email, category
   ```

3. **Create Category Templates** (Upload 8 Excel files, one per category):
   ```
   POST /api/admin/import-category-templates
   File: technical_skills.xlsx
   Form Parameter: category=Technical
   Columns: name, description, category
   
   Repeat for each category:
   - sales_skills.xlsx → category=Sales
   - hr_skills.xlsx → category=HR
   - finance_skills.xlsx → category=Finance
   - etc.
   ```

4. **Result**: 
   - Technical employees see only Technical skills
   - Sales employees see only Sales skills
   - Each category has its own skill set

## Notes

- **Category Names**: Must match exactly (case-sensitive)
- **Skill Names**: Must match master skills exactly (case-sensitive)
- **Display Order**: Lower numbers appear first
- **Required Skills**: Currently informational (can be used for validation)
- **Multiple Categories**: A skill can belong to multiple category templates

