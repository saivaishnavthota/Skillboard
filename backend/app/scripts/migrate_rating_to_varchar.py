"""Script to migrate rating columns from enum to VARCHAR."""
import sys
import os
from sqlalchemy import create_engine, text

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.database import DATABASE_URL

def migrate_rating_to_varchar():
    """Migrate rating columns from enum to VARCHAR."""
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        try:
            print("Migrating rating columns from enum to VARCHAR...")
            
            # Check if employee_skills table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'employee_skills'
                )
            """))
            if not result.fetchone()[0]:
                print("ERROR: employee_skills table does not exist!")
                return
            
            # Check current column type
            result = conn.execute(text("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'employee_skills' AND column_name = 'rating'
            """))
            row = result.fetchone()
            if not row:
                print("ERROR: rating column does not exist!")
                return
            
            current_type = row[0]
            print(f"Current rating column type: {current_type}")
            
            if current_type == 'USER-DEFINED':
                # It's an enum, need to migrate
                print("\nConverting rating column to VARCHAR...")
                conn.execute(text("ALTER TABLE employee_skills ALTER COLUMN rating TYPE VARCHAR(50) USING rating::text"))
                print("✓ Converted rating column")
            elif current_type == 'character varying' or current_type == 'varchar':
                print("✓ Rating column is already VARCHAR")
            else:
                print(f"⚠ Unexpected column type: {current_type}")
            
            # Check initial_rating column
            result = conn.execute(text("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'employee_skills' AND column_name = 'initial_rating'
            """))
            row = result.fetchone()
            if row:
                current_type = row[0]
                print(f"\nCurrent initial_rating column type: {current_type}")
                
                if current_type == 'USER-DEFINED':
                    print("Converting initial_rating column to VARCHAR...")
                    conn.execute(text("ALTER TABLE employee_skills ALTER COLUMN initial_rating TYPE VARCHAR(50) USING initial_rating::text"))
                    print("✓ Converted initial_rating column")
                elif current_type == 'character varying' or current_type == 'varchar':
                    print("✓ initial_rating column is already VARCHAR")
            
            # Check role_requirements.required_rating column
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'role_requirements'
                )
            """))
            if result.fetchone()[0]:
                result = conn.execute(text("""
                    SELECT data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'role_requirements' AND column_name = 'required_rating'
                """))
                row = result.fetchone()
                if row:
                    current_type = row[0]
                    print(f"\nCurrent required_rating column type: {current_type}")
                    
                    if current_type == 'USER-DEFINED':
                        print("Converting required_rating column to VARCHAR...")
                        conn.execute(text("ALTER TABLE role_requirements ALTER COLUMN required_rating TYPE VARCHAR(50) USING required_rating::text"))
                        print("✓ Converted required_rating column")
                    elif current_type == 'character varying' or current_type == 'varchar':
                        print("✓ required_rating column is already VARCHAR")
            
            print("\n✓ Migration complete!")
            
        except Exception as e:
            print(f"\n✗ Error during migration: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    migrate_rating_to_varchar()

