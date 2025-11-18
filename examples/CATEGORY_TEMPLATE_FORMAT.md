# Category Skill Template Format

## Overview

Category skill templates define which skills are available for each employee category. When an employee is assigned to a category, they can only see and add skills from that category's template.

## How It Works

1. **Employee Categories**: Employees are assigned a `category` field (e.g., "Technical", "Sales", "HR", "Finance")
2. **Category Templates**: Each category has a template that lists which skills are available
3. **Skill Filtering**: Employees only see skills from their category's template in the skill browser
4. **Validation**: When employees try to add skills, the system validates they're from their category template

## API Endpoints

### Get All Categories
```
GET /api/categories/
```
Returns list of all categories that have templates defined.

### Get Category Template
```
GET /api/categories/{category}/template
```
Returns all skills in a category's template.

### Add Skill to Category Template (Admin)
```
POST /api/categories/{category}/template
```
Add a skill to a category template.

**Request Body:**
```json
{
  "category": "Technical",
  "skill_id": 1,
  "is_required": false,
  "display_order": 1
}
```

### Remove Skill from Category Template (Admin)
```
DELETE /api/categories/{category}/template/{template_id}
```

## Excel Import Format

You can import category templates via Excel using the endpoint:
```
POST /api/admin/import-category-templates
```

**Important**: This endpoint accepts a category parameter. All skills in the Excel file will be assigned to that category.

### Request Format
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Parameters**:
  - `file`: Excel file (.xlsx or .xls)
  - `category`: Category name (form field) - e.g., "Technical", "Sales", "HR"

### Excel Format

Each Excel sheet should contain skills for ONE category. The category is specified as a form parameter, not in the Excel file.

| Column Name | Required | Description | Example |
|------------|----------|-------------|---------|
| **name** | ✅ Yes | Skill name (will be created in master skills if doesn't exist) | React, Python, SQL |
| **description** | ❌ No | Skill description | "React framework for building UIs" |
| **skill_category** | ❌ No | Skill grouping/tag (e.g., "Programming", "Database") - **NOT the employee category**, just for organizing skills | Programming, Database |

**Important Distinction:**
- **Form Parameter `category`** = Employee category (Technical, HR, Sales) - determines which employees see these skills
- **Excel Column `skill_category`** = Skill grouping (Programming, Database) - just for organizing skills, completely separate

### Example Excel Structure

**File: technical_skills.xlsx** (upload with category="Technical")

| name      | description              | skill_category |
|-----------|--------------------------|----------------|
| React     | React framework          | Programming    |
| Python    | Python programming       | Programming    |
| SQL       | SQL database queries     | Database       |
| JavaScript| JavaScript language       | Programming    |

**File: sales_skills.xlsx** (upload with category="Sales")

| name        | description              |
|-------------|--------------------------|
| CRM         | Customer Relationship Mgmt |
| Negotiation | Sales negotiation skills |
| Presentation| Presentation skills       |

### Usage Example

```bash
# Upload Technical skills
curl -X POST "http://localhost:8000/api/admin/import-category-templates" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@technical_skills.xlsx" \
  -F "category=Technical"

# Upload Sales skills
curl -X POST "http://localhost:8000/api/admin/import-category-templates" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@sales_skills.xlsx" \
  -F "category=Sales"
```

## Example Workflow

1. **Create Categories**: Assign categories to employees via Excel import
   - Use `category` column in employee import Excel

2. **Create Skills**: Upload master skills list
   - Use `/api/admin/upload-skills` endpoint

3. **Create Category Templates**: Define which skills belong to each category
   - Use `/api/categories/{category}/template` endpoint
   - Or use Excel import: `/api/admin/import-category-templates`

4. **Employee Experience**: 
   - Employee logs in
   - Sees only skills from their category template
   - Can only add skills from their category template

## Notes

- **Category Names**: Category names are case-sensitive strings (e.g., "Technical" ≠ "technical")
- **Skill Matching**: Skills are matched by name (must exist in master skills first)
- **Display Order**: Skills are displayed in order of `display_order` (ascending)
- **Required Skills**: `is_required` flag can be used for validation (currently informational)
- **Multiple Categories**: A skill can belong to multiple category templates

