"""API routes for importing category skill templates from Excel."""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO
from typing import List, Optional
from app.db import database, crud
from app.schemas import UploadResponse
from app.db.models import CategorySkillTemplate, Skill
from app.api.dependencies import get_admin_user
from app.db.models import User

router = APIRouter(prefix="/api/admin", tags=["admin-category-templates"])

MAX_ROWS = 10000


@router.post("/import-category-templates", response_model=UploadResponse)
async def import_category_templates(
    file: UploadFile = File(...),
    category: str = Form(..., description="Category name to assign all skills to"),
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_admin_user),
):
    """
    Upload Excel file (.xlsx or .xls) to import skills and assign them to a category template.
    
    This endpoint:
    1. Reads skills from the Excel file
    2. Creates/updates skills in the master skills list
    3. Adds all skills to the specified category template
    
    Expected Excel columns (case-insensitive):
    - name (required): Skill name
    - description (optional): Skill description
    - skill_category (optional): Skill grouping/tag (e.g., "Programming", "Database", "Cloud") - for organizing skills only, NOT the employee category
    
    Parameters:
    - category (form field): Employee category/department (e.g., "Technical", "Sales", "HR") - determines which employees can see these skills
    
    Returns:
    - rows_processed: Number of rows successfully processed
    - rows_created: Number of new skills/templates created
    - rows_updated: Number of existing skills/templates updated
    - errors: List of any errors encountered
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ["xlsx", "xls"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Expected .xlsx or .xls"
        )
    
    if not category or not category.strip():
        raise HTTPException(status_code=400, detail="Category parameter is required")
    
    category = category.strip()
    
    try:
        # Read file content
        contents = await file.read()
        
        # Parse Excel file
        df = pd.read_excel(BytesIO(contents), engine="openpyxl")
        
        # Validate row count
        if len(df) > MAX_ROWS:
            raise HTTPException(
                status_code=400,
                detail=f"File contains {len(df)} rows. Maximum allowed is {MAX_ROWS}."
            )
        
        # Normalize column names (case-insensitive)
        df.columns = df.columns.str.strip().str.lower()
        
        # Validate required columns
        if "name" not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="Missing required column: 'name' (skill name)"
            )
        
        rows_processed = 0
        rows_created = 0
        rows_updated = 0
        skills_created = 0
        templates_created = 0
        errors = []
        
        # Process each row
        for idx, row in df.iterrows():
            try:
                skill_name = str(row["name"]).strip()
                
                if not skill_name:
                    errors.append(f"Row {idx + 2}: Missing skill name")
                    continue
                
                # Get optional fields
                description = None
                if "description" in df.columns and pd.notna(row.get("description")):
                    description = str(row["description"]).strip()
                    if not description:
                        description = None
                
                # Get skill category (for organizing skills, different from employee category)
                skill_category = None
                # Check both "skill_category" and "category" for backward compatibility
                if "skill_category" in df.columns and pd.notna(row.get("skill_category")):
                    skill_category = str(row["skill_category"]).strip()
                    if not skill_category:
                        skill_category = None
                elif "category" in df.columns and pd.notna(row.get("category")):
                    # Backward compatibility: also accept "category" column
                    skill_category = str(row["category"]).strip()
                    if not skill_category:
                        skill_category = None
                
                # Create or update skill in master list
                existing_skill = crud.get_skill_by_name(db, skill_name)
                if existing_skill:
                    skill = existing_skill
                    # Update description/category if provided
                    if description is not None:
                        skill.description = description
                    if skill_category is not None:
                        skill.category = skill_category
                    if description is not None or skill_category is not None:
                        db.commit()
                        db.refresh(skill)
                    rows_updated += 1
                else:
                    # Create new skill
                    skill = crud.upsert_skill(db, skill_name, description, skill_category)
                    skills_created += 1
                    rows_created += 1
                
                # Check if template entry already exists
                existing_template = (
                    db.query(CategorySkillTemplate)
                    .filter(
                        CategorySkillTemplate.category == category,
                        CategorySkillTemplate.skill_id == skill.id
                    )
                    .first()
                )
                
                if existing_template:
                    # Template already exists, skip
                    pass
                else:
                    # Create new template entry with defaults
                    db_template = CategorySkillTemplate(
                        category=category,
                        skill_id=skill.id,
                        is_required=False,  # Default
                        display_order=None,  # Will use database default ordering
                    )
                    db.add(db_template)
                    templates_created += 1
                    rows_created += 1
                
                rows_processed += 1
                
            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")
        
        db.commit()
        
        message = f"Category template imported successfully. {rows_processed} skills processed for category '{category}'. "
        message += f"{skills_created} new skills created, {templates_created} template entries added."
        
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

