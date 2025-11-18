# Employee Import Excel Format

## File Format
- **File Type**: Excel (.xlsx or .xls)
- **Engine**: openpyxl (for .xlsx files)
- **Maximum Rows**: 10,000 rows per file

## Endpoint
```
POST /api/admin/import-users-excel
```

## Required Headers
- `Authorization: Bearer <JWT_TOKEN>` (Admin user required)
- `Content-Type: multipart/form-data`

## Excel Sheet Format

### Column Headers (Case-Insensitive)

The first row must contain column headers. Column names are case-insensitive and whitespace is automatically trimmed.

| Column Name | Required | Description | Example Values |
|------------|----------|-------------|----------------|
| **employee_id** | ✅ Yes | Unique employee identifier | E001, EMP-123, 12345 |
| **first_name** | ✅ Yes | Employee's first name | John, Jane |
| **last_name** | ✅ Yes | Employee's last name | Doe, Smith |
| **company_email** | ✅ Yes | Employee's company email (must contain @) | john.doe@company.com |
| **department** | ❌ No | Employee's department | Engineering, Sales, HR |
| **role** | ❌ No | Employee's job title | Developer, Manager, Analyst |
| **team** | ❌ No | Team assignment | consulting, technical_delivery, project_programming, corporate_functions_it, corporate_functions_marketing, corporate_functions_finance, corporate_functions_legal, corporate_functions_pc | 
| **category** | ❌ No | Employee category for skill template filtering | Technical, Sales, HR, Finance |

### Example Excel Sheet Structure

Create an Excel file with the following structure:

**Row 1 (Headers):**
```
employee_id | first_name | last_name | company_email | department | role | team | category
```

**Row 2+ (Data):**
```
E001 | John | Doe | john.doe@company.com | Engineering | Developer | technical_delivery | Technical
E002 | Jane | Smith | jane.smith@company.com | Sales | Manager | consulting | Sales
E003 | Bob | Johnson | bob.johnson@company.com | HR | HR Manager | corporate_functions_pc | HR
```

### Visual Example

```
| employee_id | first_name | last_name | company_email           | department  | role      | team                  | category   |
|-------------|------------|-----------|-------------------------|-------------|-----------|-----------------------|------------|
| E001        | John       | Doe       | john.doe@company.com    | Engineering | Developer | technical_delivery    | Technical  |
| E002        | Jane       | Smith     | jane.smith@company.com  | Sales       | Manager   | consulting            | Sales      |
| E003        | Bob        | Johnson   | bob.johnson@company.com | HR          | HR Manager| corporate_functions_pc| HR         |
```

## Notes

1. **Column Names**: Column names are case-insensitive and whitespace is trimmed
2. **Email Validation**: Basic email format validation (must contain "@")
3. **Temporary Passwords**: New users will receive temporary passwords saved to `users_import_report.csv` (DEV ONLY)
4. **User Creation**: 
   - If user with email already exists, it will be updated
   - New users are created with `is_active=False` and `must_change_password=True`
   - Users must change password on first login
5. **Maximum Rows**: 10,000 rows per file
6. **Error Handling**: Errors are reported per row in the response

## Response Format

```json
{
  "message": "Users imported successfully. 3 rows processed. 2 new users created with temp passwords...",
  "rows_processed": 3,
  "rows_created": 2,
  "rows_updated": 1,
  "errors": null
}
```

## Sample cURL Command

```bash
curl -X POST "http://localhost:8000/api/admin/import-users-excel" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@employees.xlsx"
```

## Sample Python Request

```python
import requests

url = "http://localhost:8000/api/admin/import-users-excel"
headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN"
}
files = {
    "file": ("employees.xlsx", open("employees.xlsx", "rb"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
}

response = requests.post(url, headers=headers, files=files)
print(response.json())
```

