"""API routes for admin operations (Excel uploads)."""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO
from typing import List
from app.db import database, crud
from app.schemas import UploadResponse
from app.db.models import RatingEnum

router = APIRouter(prefix="/api/admin", tags=["admin"])

MAX_ROWS = 10000


def parse_rating(rating_str: str) -> RatingEnum:
    """Parse rating string to RatingEnum."""
    if not rating_str:
        return RatingEnum.BEGINNER
    
    rating_str = str(rating_str).strip()
    rating_lower = rating_str.lower()
    
    if rating_lower in ["beginner", "beg", "b", "1"]:
        return RatingEnum.BEGINNER
    elif rating_lower in ["developing", "dev", "d", "2"]:
        return RatingEnum.DEVELOPING
    elif rating_lower in ["intermediate", "int", "i", "mid", "3"]:
        return RatingEnum.INTERMEDIATE
    elif rating_lower in ["advanced", "adv", "a", "4"]:
        return RatingEnum.ADVANCED
    elif rating_lower in ["expert", "exp", "e", "5"]:
        return RatingEnum.EXPERT
    else:
        return RatingEnum.BEGINNER


@router.post("/upload-skills", response_model=UploadResponse)
async def upload_skills(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
):
    """
    Upload Excel/CSV file to populate master skills list.
    Expected columns: name (required), description (optional)
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ["xlsx", "xls", "csv"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Expected .xlsx, .xls, or .csv"
        )

    try:
        # Read file content
        contents = await file.read()
        
        # Parse based on file type
        if file_ext == "csv":
            df = pd.read_csv(BytesIO(contents))
        else:
            df = pd.read_excel(BytesIO(contents), engine="openpyxl")

        # Normalize column names (case-insensitive, strip whitespace)
        df.columns = df.columns.str.strip().str.lower()

        # Validate row count
        if len(df) > MAX_ROWS:
            raise HTTPException(
                status_code=400,
                detail=f"File contains {len(df)} rows. Maximum allowed is {MAX_ROWS}. Please chunk your data."
            )

        # Validate required columns
        if "name" not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="Missing required column: 'name'"
            )

        rows_processed = 0
        rows_created = 0
        rows_updated = 0
        errors = []

        # Process each row
        for idx, row in df.iterrows():
            try:
                skill_name = str(row["name"]).strip()
                if not skill_name:
                    errors.append(f"Row {idx + 2}: Empty skill name")
                    continue

                description = None
                if "description" in df.columns and pd.notna(row.get("description")):
                    description = str(row["description"]).strip()
                    if not description:  # Empty string becomes None
                        description = None
                
                category = None
                if "category" in df.columns and pd.notna(row.get("category")):
                    category = str(row["category"]).strip()
                    if not category:  # Empty string becomes None
                        category = None

                # Check if skill exists
                existing = crud.get_skill_by_name(db, skill_name)
                if existing:
                    rows_updated += 1
                else:
                    rows_created += 1

                crud.upsert_skill(db, skill_name, description, category)
                rows_processed += 1

            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")

        return UploadResponse(
            message="Skills uploaded successfully",
            rows_processed=rows_processed,
            rows_created=rows_created,
            rows_updated=rows_updated,
            errors=errors if errors else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.post("/upload-employee-skills", response_model=UploadResponse)
async def upload_employee_skills(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
):
    """
    Upload Excel/CSV file to populate employee-skill mappings.
    Expected columns: EmployeeID, EmployeeName, SkillName, Rating, YearsExperience (optional)
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ["xlsx", "xls", "csv"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Expected .xlsx, .xls, or .csv"
        )

    try:
        # Read file content
        contents = await file.read()
        
        # Parse based on file type
        if file_ext == "csv":
            df = pd.read_csv(BytesIO(contents))
        else:
            df = pd.read_excel(BytesIO(contents), engine="openpyxl")

        # Validate row count
        if len(df) > MAX_ROWS:
            raise HTTPException(
                status_code=400,
                detail=f"File contains {len(df)} rows. Maximum allowed is {MAX_ROWS}. Please chunk your data."
            )

        # Validate required columns (case-insensitive)
        required_cols = ["employeeid", "employeename", "skillname", "rating"]
        df.columns = df.columns.str.lower()
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_cols)}"
            )

        rows_processed = 0
        rows_created = 0
        rows_updated = 0
        errors = []

        # Process each row
        for idx, row in df.iterrows():
            try:
                employee_id = str(row["employeeid"]).strip()
                employee_name = str(row["employeename"]).strip()
                skill_name = str(row["skillname"]).strip()
                rating_str = str(row["rating"]).strip()

                if not employee_id or not employee_name or not skill_name:
                    errors.append(f"Row {idx + 2}: Missing required fields")
                    continue

                # Parse rating
                rating = parse_rating(rating_str)

                # Parse years_experience if present
                years_experience = None
                if "yearsexperience" in df.columns and pd.notna(row.get("yearsexperience")):
                    try:
                        years_experience = float(row["yearsexperience"])
                    except (ValueError, TypeError):
                        pass

                # Upsert employee
                employee = crud.upsert_employee(db, employee_id, employee_name)

                # Upsert skill
                skill = crud.upsert_skill(db, skill_name)

                # Check if employee-skill mapping exists
                existing = crud.get_employee_skill(db, employee.id, skill.id)
                if existing:
                    rows_updated += 1
                else:
                    rows_created += 1

                # Upsert employee-skill mapping (existing skills, not interested)
                crud.upsert_employee_skill(
                    db, employee.id, skill.id, rating, years_experience, is_interested=False
                )
                rows_processed += 1

            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")

        return UploadResponse(
            message="Employee skills uploaded successfully",
            rows_processed=rows_processed,
            rows_created=rows_created,
            rows_updated=rows_updated,
            errors=errors if errors else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

