"""Script to seed users from CSV file.

Usage:
    python -m app.scripts.seed_users path/to/users.csv

This script:
1. Reads users.csv with columns: employee_id, first_name, last_name, company_email, department, role
2. Creates Employee records
3. Creates User records with temporary passwords
4. Generates users_import_report.csv with plaintext temp passwords (DEV ONLY)

WARNING: This script generates plaintext passwords. For production, use proper email service.
"""
import sys
import os
import pandas as pd
import secrets
import string
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.db import database
from app.db import crud
from app.core.security import get_password_hash


def generate_temp_password(length: int = 12) -> str:
    """Generate a random temporary password."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def seed_users(csv_path: str):
    """Seed users from CSV file."""
    # Initialize database
    database.init_db()
    db = next(database.get_db())
    
    try:
        # Read CSV
        df = pd.read_csv(csv_path)
        
        # Normalize column names
        df.columns = df.columns.str.strip().str.lower()
        
        # Validate required columns
        required_cols = ["employee_id", "first_name", "last_name", "company_email", "department", "role"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"ERROR: Missing required columns: {', '.join(missing_cols)}")
            return
        
        temp_passwords = []
        rows_processed = 0
        rows_created = 0
        errors = []
        
        # Process each row
        for idx, row in df.iterrows():
            try:
                employee_id = str(row["employee_id"]).strip()
                first_name = str(row["first_name"]).strip() if pd.notna(row.get("first_name")) else None
                last_name = str(row["last_name"]).strip() if pd.notna(row.get("last_name")) else None
                company_email = str(row["company_email"]).strip() if pd.notna(row.get("company_email")) else None
                department = str(row["department"]).strip() if pd.notna(row.get("department")) else None
                role = str(row["role"]).strip() if pd.notna(row.get("role")) else None
                
                if not employee_id or not company_email:
                    errors.append(f"Row {idx + 2}: Missing employee_id or company_email")
                    continue
                
                # Create full name
                name = f"{first_name} {last_name}".strip() if first_name and last_name else company_email.split("@")[0]
                
                # Upsert employee
                employee = crud.upsert_employee(
                    db,
                    employee_id=employee_id,
                    name=name,
                    first_name=first_name,
                    last_name=last_name,
                    company_email=company_email,
                    department=department,
                    role=role,
                )
                
                # Check if user already exists
                existing_user = crud.get_user_by_email(db, company_email)
                if existing_user:
                    print(f"User {company_email} already exists, skipping...")
                    continue
                
                # Create new user with temp password
                temp_password = generate_temp_password()
                password_hash = get_password_hash(temp_password)
                
                user_dict = {
                    "email": company_email,
                    "password_hash": password_hash,
                    "employee_id": employee_id,
                    "is_active": False,  # Set to False until password is changed
                    "is_admin": False,
                    "must_change_password": True,
                }
                
                crud.create_user(db, user_dict)
                rows_created += 1
                rows_processed += 1
                
                # Store temp password for report
                temp_passwords.append({
                    "employee_id": employee_id,
                    "email": company_email,
                    "name": name,
                    "department": department or "",
                    "role": role or "",
                    "temp_password": temp_password,
                })
                
                print(f"Created user: {company_email} ({employee_id})")
                
            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")
                print(f"ERROR Row {idx + 2}: {str(e)}")
        
        # Generate import report
        if temp_passwords:
            report_df = pd.DataFrame(temp_passwords)
            report_path = "users_import_report.csv"
            report_df.to_csv(report_path, index=False)
            print(f"\n✓ Generated {report_path} with {len(temp_passwords)} temp passwords")
            print("⚠ WARNING: This file contains plaintext passwords. For DEV ONLY.")
            print("⚠ In production, send passwords via secure email service.")
        else:
            print("\nNo new users created.")
        
        if errors:
            print(f"\n⚠ {len(errors)} errors occurred:")
            for error in errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more errors")
        
        print(f"\n✓ Processed {rows_processed} rows, created {rows_created} users")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.scripts.seed_users path/to/users.csv")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    if not os.path.exists(csv_path):
        print(f"ERROR: File not found: {csv_path}")
        sys.exit(1)
    
    seed_users(csv_path)

