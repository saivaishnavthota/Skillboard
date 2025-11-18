"""API routes for skills management."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import database, crud
from app.schemas import Skill, SkillCreate
from app.api.dependencies import get_optional_current_user
from app.db.models import User, CategorySkillTemplate, Skill as SkillModel

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("/", response_model=List[Skill])
def get_skills(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,  # Filter by category template
    db: Session = Depends(database.get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Get skills. If user is logged in and has a category, returns only skills from their category template.
    If category parameter is provided, returns skills from that category template.
    Otherwise, returns all skills.
    """
    # If user is logged in, try to get their category
    employee_category = None
    if current_user and current_user.employee_id:
        employee = crud.get_employee_by_id(db, current_user.employee_id)
        if employee and employee.category:
            employee_category = employee.category
    
    # Use provided category or employee's category
    filter_category = category or employee_category
    
    if filter_category:
        # Get skills from category template
        template_skills = (
            db.query(CategorySkillTemplate, SkillModel)
            .join(SkillModel, CategorySkillTemplate.skill_id == SkillModel.id)
            .filter(CategorySkillTemplate.category == filter_category)
            .order_by(CategorySkillTemplate.display_order.asc().nullslast(), SkillModel.name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [skill for _, skill in template_skills]
    else:
        # Return all skills if no category filter
        skills = crud.get_all_skills(db, skip=skip, limit=limit)
        return skills


@router.get("/{skill_id}", response_model=Skill)
def get_skill(skill_id: int, db: Session = Depends(database.get_db)):
    """Get a skill by ID."""
    skill = crud.get_skill_by_id(db, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.post("/", response_model=Skill)
def create_skill(skill: SkillCreate, db: Session = Depends(database.get_db)):
    """Create a new skill."""
    # Check if skill already exists
    existing = crud.get_skill_by_name(db, skill.name)
    if existing:
        raise HTTPException(status_code=400, detail="Skill already exists")
    return crud.create_skill(db, skill.model_dump())

