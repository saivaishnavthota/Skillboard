"""Script to update ratingenum PostgreSQL enum type to include Developing and Expert."""
import sys
import os
from sqlalchemy import create_engine, text

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.database import DATABASE_URL

def update_rating_enum():
    """Update ratingenum enum type to include new values."""
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        try:
            # Check current enum values
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
                print("Adding 'Developing' to ratingenum...")
                conn.execute(text("ALTER TYPE ratingenum ADD VALUE 'Developing'"))
                print("✓ Added 'Developing'")
            else:
                print("✓ 'Developing' already exists")
            
            # Add 'Expert' if it doesn't exist
            if 'Expert' not in enum_values:
                print("Adding 'Expert' to ratingenum...")
                conn.execute(text("ALTER TYPE ratingenum ADD VALUE 'Expert'"))
                print("✓ Added 'Expert'")
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
            print("\n✓ Enum update complete!")
            
        except Exception as e:
            print(f"Error updating enum: {e}")
            raise

if __name__ == "__main__":
    update_rating_enum()

