# Database Access Guide

## Database Connection Details

Based on `docker-compose.yml`:
- **Container Name**: `skillboard-postgres`
- **User**: `skillboard`
- **Password**: `skillboard`
- **Database**: `skillboard`
- **Port**: 5432 (inside container)

## Access Methods

### Method 1: Using Docker Exec (Recommended)

Access the database directly from the Docker container:

```bash
docker exec -it skillboard-postgres psql -U skillboard -d skillboard
```

Or using docker-compose:

```bash
docker-compose exec postgres psql -U skillboard -d skillboard
```

### Method 2: From Host Machine (if port is exposed)

If the port is properly mapped in docker-compose.yml, you can connect from your host machine:

```bash
psql -h localhost -p 5433 -U skillboard -d skillboard
```

**Note**: You'll be prompted for the password: `skillboard`

### Method 3: Using Connection String

You can also use the connection string format:

```bash
psql postgresql://skillboard:skillboard@localhost:5433/skillboard
```

## Common PostgreSQL Commands

Once connected, you can use standard SQL commands:

```sql
-- List all tables
\dt

-- Describe a table structure
\d employees
\d skills
\d category_skill_templates

-- View all employees
SELECT * FROM employees;

-- View all skills
SELECT * FROM skills;

-- View category templates
SELECT * FROM category_skill_templates;

-- View users
SELECT id, email, employee_id, is_admin FROM users;

-- Exit
\q
```

## Useful Queries

### Check Employee Categories
```sql
SELECT DISTINCT category FROM employees WHERE category IS NOT NULL;
```

### Check Category Templates
```sql
SELECT DISTINCT category FROM category_skill_templates;
```

### View Skills by Employee Category
```sql
SELECT 
    cst.category as employee_category,
    s.name as skill_name,
    s.category as skill_category
FROM category_skill_templates cst
JOIN skills s ON cst.skill_id = s.id
ORDER BY cst.category, s.name;
```

### Count Skills per Category
```sql
SELECT 
    category as employee_category,
    COUNT(*) as skill_count
FROM category_skill_templates
GROUP BY category
ORDER BY skill_count DESC;
```

## Troubleshooting

### If port connection fails:
Check if the port mapping in `docker-compose.yml` is correct. It should be:
```yaml
ports:
  - "5433:5432"  # Host:Container
```

### If container name is different:
Check your running containers:
```bash
docker ps
```

Then use the correct container name in the exec command.

### Reset Database (WARNING: Deletes all data)
```bash
docker-compose down -v
docker-compose up -d
```

