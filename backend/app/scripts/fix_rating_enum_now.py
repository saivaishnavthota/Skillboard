"""Script to forcefully update ratingenum PostgreSQL enum type."""
import sys
import os
from sqlalchemy import create_engine, text

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.database import DATABASE_URL

def fix_rating_enum():
    """Force update ratingenum enum type to include new values."""
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        try:
            # Check if enum exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_type WHERE typname = 'ratingenum'
                )
            """))
            enum_exists = result.fetchone()[0]
            
            if not enum_exists:
                print("ERROR: ratingenum type does not exist!")
                return
            
            # Get current enum values
            result = conn.execute(text("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'ratingenum')
                ORDER BY enumsortorder
            """))
            enum_values = [row[0] for row in result.fetchall()]
            print(f"Current enum values: {enum_values}")
            
            # Add 'Developing' if it doesn't exist
            if 'Developing' not in enum_values:
                print("\nAdding 'Developing' to ratingenum...")
                try:
                    conn.execute(text("ALTER TYPE ratingenum ADD VALUE IF NOT EXISTS 'Developing'"))
                    print("✓ Added 'Developing'")
                except Exception as e:
                    # Try without IF NOT EXISTS (older PostgreSQL versions)
                    try:
                        conn.execute(text("ALTER TYPE ratingenum ADD VALUE 'Developing'"))
                        print("✓ Added 'Developing'")
                    except Exception as e2:
                        print(f"✗ Could not add 'Developing': {e2}")
            else:
                print("✓ 'Developing' already exists")
            
            # Add 'Expert' if it doesn't exist
            if 'Expert' not in enum_values:
                print("\nAdding 'Expert' to ratingenum...")
                try:
                    conn.execute(text("ALTER TYPE ratingenum ADD VALUE IF NOT EXISTS 'Expert'"))
                    print("✓ Added 'Expert'")
                except Exception as e:
                    # Try without IF NOT EXISTS (older PostgreSQL versions)
                    try:
                        conn.execute(text("ALTER TYPE ratingenum ADD VALUE 'Expert'"))
                        print("✓ Added 'Expert'")
                    except Exception as e2:
                        print(f"✗ Could not add 'Expert': {e2}")
            else:
                print("✓ 'Expert' already exists")
            
            # Verify final state
            result = conn.execute(text("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'ratingenum')
                ORDER BY enumsortorder
            """))
            final_values = [row[0] for row in result.fetchall()]
            print(f"\nFinal enum values: {final_values}")
            
            # Check if all required values are present
            required = ['Beginner', 'Developing', 'Intermediate', 'Advanced', 'Expert']
            missing = [v for v in required if v not in final_values]
            if missing:
                print(f"\n⚠ WARNING: Missing enum values: {missing}")
            else:
                print("\n✓ All required enum values are present!")
            
        except Exception as e:
            print(f"\n✗ Error updating enum: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    fix_rating_enum()

