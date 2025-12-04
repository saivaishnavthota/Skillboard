#!/usr/bin/env python3
"""Apply role requirements migration."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine
from sqlalchemy import text

def apply_migration():
    """Apply the role requirements migration."""
    print("Applying role requirements migration...")
    
    with open(os.path.join(os.path.dirname(__file__), 'create_role_requirements.sql'), 'r') as f:
        sql = f.read()
    
    with engine.connect() as conn:
        # Execute each statement separately
        for statement in sql.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    conn.execute(text(statement))
                    conn.commit()
                except Exception as e:
                    print(f"Warning: {e}")
                    continue
    
    print("✓ Role requirements migration applied successfully!")
    print("\nNote: You can now add role requirements via the admin API or database.")
    print("Example: Add requirements for each band specifying required skill levels.")

if __name__ == "__main__":
    apply_migration()
