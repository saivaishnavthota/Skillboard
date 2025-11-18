# Category Template Excel Import - Quick Reference

## Endpoint
```
POST /api/admin/import-category-templates
```

## How It Works

1. **Prepare 8 Excel Files**: One file per category (Technical, Sales, HR, Finance, etc.)
2. **Each File Contains**: List of skills for that category
3. **Upload with Category**: Specify the category as a form parameter
4. **Result**: All skills in the file are:
   - Added to master skills (if new)
   - Assigned to the specified category template

## Excel File Format

### Required Column
- **name** - Skill name (will be created if doesn't exist)

### Optional Columns
- **description** - Skill description
- **skill_category** - Skill grouping/tag (e.g., "Programming", "Database", "Cloud") - **NOT the employee category**, just for organizing skills

**Important**: The `category` form parameter (when uploading) is the **Employee Category** (Technical, HR, Sales). The `skill_category` column in Excel is just for organizing skills and is completely separate.

### Example: Technical Skills File

**File Name**: `technical_skills.xlsx`

| name        | description              | skill_category |
|-------------|--------------------------|----------------|
| React       | React framework          | Programming    |
| Python      | Python programming       | Programming    |
| JavaScript  | JavaScript language       | Programming    |
| SQL         | SQL database queries     | Database       |
| Docker      | Containerization         | DevOps         |
| AWS         | Amazon Web Services      | Cloud          |

**Note**: The `skill_category` column is optional and just for organizing skills. The actual employee category is specified as a form parameter when uploading.

**Upload Command:**
```bash
curl -X POST "http://localhost:8000/api/admin/import-category-templates" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@technical_skills.xlsx" \
  -F "category=Technical"
```

### Example: Sales Skills File

**File Name**: `sales_skills.xlsx`

| name         | description              |
|--------------|--------------------------|
| CRM          | Customer Relationship Mgmt |
| Negotiation  | Sales negotiation        |
| Presentation | Presentation skills      |
| Lead Gen     | Lead generation          |

**Upload Command:**
```bash
curl -X POST "http://localhost:8000/api/admin/import-category-templates" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@sales_skills.xlsx" \
  -F "category=Sales"
```

## Python Example

```python
import requests

base_url = "http://localhost:8000/api/admin/import-category-templates"
token = "YOUR_JWT_TOKEN"

categories = {
    "technical_skills.xlsx": "Technical",
    "sales_skills.xlsx": "Sales",
    "hr_skills.xlsx": "HR",
    "finance_skills.xlsx": "Finance",
    "marketing_skills.xlsx": "Marketing",
    "legal_skills.xlsx": "Legal",
    "it_skills.xlsx": "IT",
    "operations_skills.xlsx": "Operations"
}

for filename, category in categories.items():
    with open(filename, 'rb') as f:
        files = {'file': (filename, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        data = {'category': category}
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.post(base_url, headers=headers, files=files, data=data)
        print(f"{category}: {response.json()}")
```

## Notes

- **Category Parameter**: Must be provided as form data, not in Excel
- **Skill Creation**: Skills are automatically created if they don't exist
- **Multiple Uploads**: Upload each category file separately
- **Updates**: If skill already exists, description/category are updated
- **Template**: If skill already in template, it will be skipped (no duplicate entries)

