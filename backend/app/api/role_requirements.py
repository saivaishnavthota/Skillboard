"""API routes for managing role requirements (band-based skill requirements)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import database
from app.db.models import RoleRequirement, Skill, RatingEnum
from app.api.dependencies import get_admin_user, User
from pydantic import BaseModel

router = APIRouter(prefix="/api/role-requirements", tags=["role-requirements"])


class RoleRequirementCreate(BaseModel):
    band: str
    skill_id: int
    required_rating: RatingEnum
    is_required: bool = True


class RoleRequirementResponse(BaseModel):
    id: int
    band: str
    skill_id: int
    skill_name: str
    required_rating: str
    is_required: bool

    class Config:
        from_attributes = True


@router.post("", response_model=RoleRequirementResponse)
def create_role_requirement(
    requirement: RoleRequirementCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_admin_user),
):
    """Create a new role requirement (admin only)."""
    # Verify skill exists
    skill = db.query(Skill).filter(Skill.id == requirement.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # Check if requirement already exists
    existing = db.query(RoleRequirement).filter(
        RoleRequirement.band == requirement.band,
        RoleRequirement.skill_id == requirement.skill_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Role requirement already exists for this band and skill")
    
    db_requirement = RoleRequirement(
        band=requirement.band,
        skill_id=requirement.skill_id,
        required_rating=requirement.required_rating,
        is_required=requirement.is_required,
    )
    db.add(db_requirement)
    db.commit()
    db.refresh(db_requirement)
    
    return RoleRequirementResponse(
        id=db_requirement.id,
        band=db_requirement.band,
        skill_id=db_requirement.skill_id,
        skill_name=skill.name,
        required_rating=db_requirement.required_rating.value,
        is_required=db_requirement.is_required,
    )


@router.get("", response_model=List[RoleRequirementResponse])
def get_role_requirements(
    band: Optional[str] = None,
    skill_id: Optional[int] = None,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_admin_user),
):
    """Get all role requirements with optional filters (admin only)."""
    query = db.query(RoleRequirement)
    
    if band:
        query = query.filter(RoleRequirement.band == band)
    if skill_id:
        query = query.filter(RoleRequirement.skill_id == skill_id)
    
    requirements = query.all()
    
    result = []
    for req in requirements:
        skill = db.query(Skill).filter(Skill.id == req.skill_id).first()
        result.append(RoleRequirementResponse(
            id=req.id,
            band=req.band,
            skill_id=req.skill_id,
            skill_name=skill.name if skill else "Unknown",
            required_rating=req.required_rating.value,
            is_required=req.is_required,
        ))
    
    return result


@router.put("/{requirement_id}", response_model=RoleRequirementResponse)
def update_role_requirement(
    requirement_id: int,
    update: RoleRequirementCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_admin_user),
):
    """Update a role requirement (admin only)."""
    requirement = db.query(RoleRequirement).filter(RoleRequirement.id == requirement_id).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Role requirement not found")
    
    # Verify skill exists
    skill = db.query(Skill).filter(Skill.id == update.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    requirement.band = update.band
    requirement.skill_id = update.skill_id
    requirement.required_rating = update.required_rating
    requirement.is_required = update.is_required
    
    db.commit()
    db.refresh(requirement)
    
    return RoleRequirementResponse(
        id=requirement.id,
        band=requirement.band,
        skill_id=requirement.skill_id,
        skill_name=skill.name,
        required_rating=requirement.required_rating.value,
        is_required=requirement.is_required,
    )


@router.delete("/{requirement_id}")
def delete_role_requirement(
    requirement_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_admin_user),
):
    """Delete a role requirement (admin only)."""
    requirement = db.query(RoleRequirement).filter(RoleRequirement.id == requirement_id).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Role requirement not found")
    
    db.delete(requirement)
    db.commit()
    
    return {"message": "Role requirement deleted successfully"}
