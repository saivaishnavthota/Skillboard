"""Add is_custom column to employee_skills table."""
import sys
import os
from sqlalchemy import create_engine, text

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import DATABASE_URL


def add_is_custom_column():
    """Add is_custom column to employee_skills table."""
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        try:
            print("Adding is_custom column to employee_skills table...")
            
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='employee_skills' AND column_name='is_custom'
            """))
            
            if result.fetchone() is None:
                print("Adding is_custom column...")
                conn.execute(text("""
                    ALTER TABLE employee_skills 
                    ADD COLUMN is_custom BOOLEAN NOT NULL DEFAULT FALSE
                """))
                print("✓ is_custom column added successfully")
            else:
                print("✓ is_custom column already exists")
            
            print("\n✓ Migration complete!")
            
        except Exception as e:
            print(f"\n✗ Error during migration: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    print("Running migration: add_is_custom_to_employee_skills")
    add_is_custom_column()
    print("Migration completed successfully!")
