"""Script to delete all skills from the database.

WARNING: This will delete all skills and all employee-skill mappings.
Use this when you want to start fresh with categorized skills.

Usage:
    # Delete all skills (inside Docker)
    docker-compose exec backend python -m app.scripts.delete_all_skills
    
    # Or from host
    python -m app.scripts.delete_all_skills
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Override DATABASE_URL if not set and running on host (not in Docker)
if not os.getenv("DATABASE_URL"):
    # Check if we're likely running on host (postgres hostname won't resolve)
    # Use localhost:5433 for host machine, postgres:5432 for Docker
    import socket
    try:
        socket.gethostbyname("postgres")
        # postgres hostname resolves, we're in Docker
        os.environ["DATABASE_URL"] = "postgresql://skillboard:skillboard@postgres:5432/skillboard"
    except socket.gaierror:
        # postgres hostname doesn't resolve, we're on host machine
        os.environ["DATABASE_URL"] = "postgresql://skillboard:skillboard@localhost:5433/skillboard"

from app.db import database
from app.db.models import Skill, EmployeeSkill
from sqlalchemy import text


def delete_all_skills():
    """Delete all skills and employee-skill mappings from the database."""
    # Initialize database
    database.init_db()
    db = next(database.get_db())
    
    try:
        # Count before deletion
        skill_count = db.query(Skill).count()
        employee_skill_count = db.query(EmployeeSkill).count()
        
        print(f"Found {skill_count} skills and {employee_skill_count} employee-skill mappings")
        
        if skill_count == 0:
            print("No skills to delete.")
            return
        
        # Confirm deletion
        print("\n⚠ WARNING: This will delete:")
        print(f"  - {skill_count} skills")
        print(f"  - {employee_skill_count} employee-skill mappings")
        print("\nThis action cannot be undone!")
        
        # Delete employee-skill mappings first (due to foreign key constraint)
        deleted_mappings = db.query(EmployeeSkill).delete()
        db.commit()
        print(f"\n✓ Deleted {deleted_mappings} employee-skill mappings")
        
        # Delete all skills
        deleted_skills = db.query(Skill).delete()
        db.commit()
        print(f"✓ Deleted {deleted_skills} skills")
        
        print("\n✓ All skills have been deleted. You can now import new skills with categories.")
        
    except Exception as e:
        db.rollback()
        print(f"✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    delete_all_skills()

