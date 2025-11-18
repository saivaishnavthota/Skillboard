"""Script to create or promote a user to admin.

Usage:
    # Create a new admin user (inside Docker container)
    docker-compose exec backend python -m app.scripts.create_admin --email admin@company.com --password admin123
    
    # Or from host (set DATABASE_URL first)
    set DATABASE_URL=postgresql://skillboard:skillboard@localhost:5433/skillboard
    python -m app.scripts.create_admin --email admin@company.com --password admin123
    
    # Promote existing user to admin
    docker-compose exec backend python -m app.scripts.create_admin --email existing@company.com --promote
"""

import sys
import os
import argparse
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
from app.db import crud
from app.core.security import get_password_hash


def create_admin_user(email: str, password: str, promote: bool = False):
    """Create a new admin user or promote an existing user to admin."""
    # Initialize database
    database.init_db()
    db = next(database.get_db())
    
    try:
        # Check if user exists
        existing_user = crud.get_user_by_email(db, email)
        
        if existing_user:
            if promote:
                # Promote existing user to admin
                updated_user = crud.update_user(
                    db,
                    existing_user.id,
                    {
                        "is_admin": True,
                        "is_active": True,
                    }
                )
                if updated_user:
                    print(f"✓ User {email} has been promoted to admin")
                    print(f"  User ID: {updated_user.id}")
                    print(f"  Email: {updated_user.email}")
                    print(f"  Is Admin: {updated_user.is_admin}")
                    print(f"  Is Active: {updated_user.is_active}")
                else:
                    print(f"✗ Failed to promote user {email}")
            else:
                print(f"✗ User {email} already exists. Use --promote to make them admin.")
                print(f"  Or use a different email address.")
                return
        else:
            if promote:
                print(f"✗ User {email} does not exist. Cannot promote.")
                print(f"  Create the user first, or remove --promote flag to create a new admin user.")
                return
            
            # Create new admin user
            password_hash = get_password_hash(password)
            user_dict = {
                "email": email,
                "password_hash": password_hash,
                "employee_id": None,  # Admin may not have employee_id
                "is_active": True,
                "is_admin": True,
                "must_change_password": False,
            }
            
            user = crud.create_user(db, user_dict)
            print(f"✓ Admin user created successfully!")
            print(f"  User ID: {user.id}")
            print(f"  Email: {user.email}")
            print(f"  Password: {password}")
            print(f"  Is Admin: {user.is_admin}")
            print(f"  Is Active: {user.is_active}")
            print(f"\n⚠ You can now log in with:")
            print(f"  Email: {email}")
            print(f"  Password: {password}")
            
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create or promote a user to admin")
    parser.add_argument("--email", required=True, help="User email address")
    parser.add_argument("--password", help="Password for new user (required if not promoting)")
    parser.add_argument("--promote", action="store_true", help="Promote existing user to admin")
    
    args = parser.parse_args()
    
    if not args.promote and not args.password:
        print("✗ ERROR: --password is required when creating a new admin user")
        print("   Use --promote to promote an existing user instead")
        sys.exit(1)
    
    create_admin_user(args.email, args.password or "", args.promote)

