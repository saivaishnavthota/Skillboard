"""Migration script to add new columns to employees table.

Run this script to add the new columns to the existing employees table:
    python -m app.scripts.migrate_add_employee_fields

Or drop and recreate tables (dev only):
    Drop the database and restart the backend - it will auto-create tables.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.db.database import engine


def migrate_employees_table():
    """Add new columns to employees table if they don't exist."""
    try:
        # Check if columns exist and add them if they don't
        with engine.begin() as conn:  # Use begin() for auto-commit
            # Check and add first_name
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='employees' AND column_name='first_name'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE employees ADD COLUMN first_name VARCHAR"))
                print("✓ Added first_name column")
            
            # Check and add last_name
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='employees' AND column_name='last_name'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE employees ADD COLUMN last_name VARCHAR"))
                print("✓ Added last_name column")
            
            # Check and add company_email
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='employees' AND column_name='company_email'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE employees ADD COLUMN company_email VARCHAR"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_employees_company_email ON employees(company_email)"))
                print("✓ Added company_email column")
            
            # Check and add department
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='employees' AND column_name='department'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE employees ADD COLUMN department VARCHAR"))
                print("✓ Added department column")
            
            # Check and add role
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='employees' AND column_name='role'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE employees ADD COLUMN role VARCHAR"))
                print("✓ Added role column")
            
            # Migrate employee_skills table
            print("\nMigrating employee_skills table...")
            
            # Check and add is_interested
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='employee_skills' AND column_name='is_interested'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE employee_skills ADD COLUMN is_interested BOOLEAN DEFAULT FALSE NOT NULL"))
                print("✓ Added is_interested column to employee_skills")
            
            # Check and add notes
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='employee_skills' AND column_name='notes'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE employee_skills ADD COLUMN notes VARCHAR"))
                print("✓ Added notes column to employee_skills")
            
            # Check and add match_score
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='employee_skills' AND column_name='match_score'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE employee_skills ADD COLUMN match_score FLOAT"))
                print("✓ Added match_score column to employee_skills")
            
            # Check and add needs_review
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='employee_skills' AND column_name='needs_review'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE employee_skills ADD COLUMN needs_review BOOLEAN DEFAULT FALSE NOT NULL"))
                print("✓ Added needs_review column to employee_skills")
            
            print("\n✓ Migration completed successfully!")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    migrate_employees_table()

