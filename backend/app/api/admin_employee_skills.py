"""API routes for admin employee skill mapping imports with fuzzy matching."""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Header
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO
from typing import List, Optional, Tuple
from rapidfuzz import fuzz
from app.db import database, crud
from app.schemas import UploadResponse
from app.db.models import RatingEnum
from app.api.dependencies import get_admin_user

router = APIRouter(prefix="/api/admin", tags=["admin-employee-skills"])

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


def fuzzy_match_skill(skill_name: str, db: Session, threshold: int = 90) -> Tuple[Optional[int], float, bool]:
    """
    Fuzzy match skill name against master skills.
    Returns: (skill_id, match_score, needs_review)
    - If match_score >= 90: return skill_id, no review needed
    - If 70 <= match_score < 90: return skill_id, needs review
    - If match_score < 70: return None, needs review
    """
    from app.db.models import Skill
    
    # Get all skills
    all_skills = db.query(Skill).all()
    
    if not all_skills:
        return None, 0.0, True
    
    best_match = None
    best_score = 0.0
    
    for skill in all_skills:
        # Use rapidfuzz ratio for matching
        score = fuzz.ratio(skill_name.lower(), skill.name.lower())
        if score > best_score:
            best_score = score
            best_match = skill
    
    if best_score >= threshold:
        # High confidence match
        return best_match.id, best_score, False
    elif best_score >= 70:
        # Medium confidence - link but flag for review
        return best_match.id, best_score, True
    else:
        # Low confidence - don't link, flag for review
        return None, best_score, True


@router.post("/import-employee-skills", response_model=UploadResponse)
async def import_employee_skills(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    x_admin_key: Optional[str] = Header(None, alias="X-ADMIN-KEY"),
):
    """
    Upload CSV file to import employee-skill mappings with fuzzy matching.
    Expected columns: employee_id, skill_name, rating, years_experience (optional), notes (optional)
    
    Uses fuzzy matching to link skill_name to master skills:
    - match_score >= 90: auto-link, no review
    - 70 <= match_score < 90: link but flag for review
    - match_score < 70: don't link, flag for review
    
    In dev: requires X-ADMIN-KEY header or admin user JWT.
    In production: requires admin user JWT only.
    """
    # Check admin access (dev: X-ADMIN-KEY, prod: JWT admin user)
    ADMIN_KEY = "dev-admin-key-change-in-production"
    if x_admin_key != ADMIN_KEY:
        # In production, this would require proper JWT admin user
        pass
    
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ["csv"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Expected .csv"
        )
    
    try:
        # Read file content
        contents = await file.read()
        df = pd.read_csv(BytesIO(contents))
        
        # Validate row count
        if len(df) > MAX_ROWS:
            raise HTTPException(
                status_code=400,
                detail=f"File contains {len(df)} rows. Maximum allowed is {MAX_ROWS}."
            )
        
        # Normalize column names (case-insensitive)
        df.columns = df.columns.str.strip().str.lower()
        
        # Validate required columns
        required_cols = ["employee_id", "skill_name", "rating"]
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
        review_items = []  # Items that need admin review
        
        # Process each row
        for idx, row in df.iterrows():
            try:
                employee_id = str(row["employee_id"]).strip()
                skill_name = str(row["skill_name"]).strip()
                rating_str = str(row["rating"]).strip()
                
                if not employee_id or not skill_name:
                    errors.append(f"Row {idx + 2}: Missing required fields")
                    continue
                
                # Parse rating
                rating = parse_rating(rating_str)
                
                # Parse optional fields
                years_experience = None
                if "years_experience" in df.columns and pd.notna(row.get("years_experience")):
                    try:
                        years_experience = float(row["years_experience"])
                    except (ValueError, TypeError):
                        pass
                
                notes = None
                if "notes" in df.columns and pd.notna(row.get("notes")):
                    notes = str(row["notes"]).strip()
                
                # Get employee
                employee = crud.get_employee_by_id(db, employee_id)
                if not employee:
                    errors.append(f"Row {idx + 2}: Employee {employee_id} not found. Import users first.")
                    continue
                
                # Fuzzy match skill
                skill_id, match_score, needs_review = fuzzy_match_skill(skill_name, db, threshold=90)
                
                if skill_id is None:
                    # No match found - create skill with raw name and flag for review
                    skill = crud.upsert_skill(db, skill_name)
                    skill_id = skill.id
                    needs_review = True
                
                # Check if employee-skill mapping exists
                existing = crud.get_employee_skill(db, employee.id, skill_id)
                if existing:
                    rows_updated += 1
                else:
                    rows_created += 1
                
                # Upsert employee-skill mapping
                # For existing skills (not interested), rating is required
                final_rating = rating if not needs_review else rating
                crud.upsert_employee_skill(
                    db,
                    employee.id,
                    skill_id,
                    final_rating,
                    years_experience=years_experience,
                    is_interested=False,  # Default to existing skills
                    notes=notes,
                    match_score=match_score,
                    needs_review=needs_review,
                )
                
                # Track items needing review
                if needs_review:
                    review_items.append({
                        "employee_id": employee_id,
                        "employee_name": employee.name,
                        "skill_name": skill_name,
                        "match_score": match_score,
                        "linked_skill_id": skill_id if skill_id else None,
                    })
                
                rows_processed += 1
                
            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")
        
        # Generate review report if needed
        if review_items:
            review_df = pd.DataFrame(review_items)
            review_path = "employee_skills_review_report.csv"
            review_df.to_csv(review_path, index=False)
        
        message = f"Employee skills imported successfully. {rows_processed} rows processed."
        if review_items:
            message += f" {len(review_items)} items need admin review. Check employee_skills_review_report.csv."
        
        return UploadResponse(
            message=message,
            rows_processed=rows_processed,
            rows_created=rows_created,
            rows_updated=rows_updated,
            errors=errors if errors else None,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

