"""API routes for category management and category skill templates."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import database, crud
from app.db.models import CategorySkillTemplate, Skill, Employee
from app.api.dependencies import get_admin_user
from app.db.models import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/categories", tags=["categories"])


class CategorySkillTemplateCreate(BaseModel):
    category: str
    skill_id: int
    is_required: bool = False
    display_order: Optional[int] = None


class CategorySkillTemplateResponse(BaseModel):
    id: int
    category: str
    skill_id: int
    is_required: bool
    display_order: Optional[int]
    skill: dict

    class Config:
        from_attributes = True


@router.get("/", response_model=List[str])
def get_categories(db: Session = Depends(database.get_db)):
    """Get list of all categories that have templates."""
    categories = (
        db.query(CategorySkillTemplate.category)
        .distinct()
        .all()
    )
    return [cat[0] for cat in categories]


@router.post("/create", response_model=dict)
def create_category(
    category_name: str = Query(..., description="Category name to create"),
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_admin_user),
):
    """Create a new empty category (admin only)."""
    category_name = category_name.strip()
    if not category_name:
        raise HTTPException(status_code=400, detail="Category name cannot be empty")
    
    # Check if category already exists
    existing = (
        db.query(CategorySkillTemplate.category)
        .filter(CategorySkillTemplate.category == category_name)
        .first()
    )
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Category '{category_name}' already exists")
    
    return {"message": f"Category '{category_name}' created successfully", "category": category_name}


@router.get("/{category}/template", response_model=List[CategorySkillTemplateResponse])
def get_category_template(
    category: str,
    db: Session = Depends(database.get_db),
):
    """Get skill template for a specific category."""
    templates = (
        db.query(CategorySkillTemplate)
        .filter(CategorySkillTemplate.category == category)
        .order_by(CategorySkillTemplate.display_order.asc().nullslast(), CategorySkillTemplate.id.asc())
        .all()
    )
    
    result = []
    for template in templates:
        skill = db.query(Skill).filter(Skill.id == template.skill_id).first()
        result.append({
            "id": template.id,
            "category": template.category,
            "skill_id": template.skill_id,
            "is_required": template.is_required,
            "display_order": template.display_order,
            "skill": {
                "id": skill.id,
                "name": skill.name,
                "description": skill.description,
                "category": skill.category,
            } if skill else None,
        })
    
    return result


@router.post("/{category}/template", response_model=CategorySkillTemplateResponse)
def create_category_template(
    category: str,
    template: CategorySkillTemplateCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_admin_user),
):
    """Create a skill template entry for a category (admin only)."""
    if template.category != category:
        raise HTTPException(status_code=400, detail="Category mismatch in URL and body")
    
    # Verify skill exists
    skill = db.query(Skill).filter(Skill.id == template.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # Check if template already exists
    existing = (
        db.query(CategorySkillTemplate)
        .filter(
            CategorySkillTemplate.category == category,
            CategorySkillTemplate.skill_id == template.skill_id
        )
        .first()
    )
    
    if existing:
        raise HTTPException(status_code=400, detail="Template entry already exists for this category and skill")
    
    # Create template
    db_template = CategorySkillTemplate(
        category=category,
        skill_id=template.skill_id,
        is_required=template.is_required,
        display_order=template.display_order,
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return {
        "id": db_template.id,
        "category": db_template.category,
        "skill_id": db_template.skill_id,
        "is_required": db_template.is_required,
        "display_order": db_template.display_order,
        "skill": {
            "id": skill.id,
            "name": skill.name,
            "description": skill.description,
            "category": skill.category,
        },
    }


@router.patch("/{category}/template/{template_id}/mandatory")
def update_template_mandatory(
    category: str,
    template_id: int,
    is_required: bool = Query(..., description="Whether the skill is mandatory"),
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_admin_user),
):
    """Update mandatory status of a skill template (admin only)."""
    from app.db.models import EmployeeSkill
    
    template = (
        db.query(CategorySkillTemplate)
        .filter(
            CategorySkillTemplate.id == template_id,
            CategorySkillTemplate.category == category
        )
        .first()
    )
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    template.is_required = is_required
    
    # If marking as mandatory, add skill to all employees in this category at Beginner level
    if is_required:
        employees = db.query(Employee).filter(Employee.category == category).all()
        added_count = 0
        
        for emp in employees:
            # Check if employee already has this skill
            existing_skill = (
                db.query(EmployeeSkill)
                .filter(
                    EmployeeSkill.employee_id == emp.id,
                    EmployeeSkill.skill_id == template.skill_id
                )
                .first()
            )
            
            if not existing_skill:
                # Add skill at Beginner level
                new_skill = EmployeeSkill(
                    employee_id=emp.id,
                    skill_id=template.skill_id,
                    rating="Beginner",
                    is_interested=False,
                )
                db.add(new_skill)
                added_count += 1
        
        db.commit()
        return {
            "message": f"Skill marked as mandatory and added to {added_count} employees at Beginner level",
            "employees_updated": added_count
        }
    
    db.commit()
    return {"message": "Skill mandatory status updated"}


@router.delete("/{category}/template/{template_id}")
def delete_category_template(
    category: str,
    template_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_admin_user),
):
    """Delete a skill template entry for a category (admin only)."""
    template = (
        db.query(CategorySkillTemplate)
        .filter(
            CategorySkillTemplate.id == template_id,
            CategorySkillTemplate.category == category
        )
        .first()
    )
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(template)
    db.commit()
    
    return {"message": "Template deleted successfully"}


@router.get("/employees/by-category")
def get_employees_by_category(
    category: str = Query(..., description="Category name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(database.get_db),
):
    """Get employees by category."""
    employees = (
        db.query(Employee)
        .filter(Employee.category == category)
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return [
        {
            "id": emp.id,
            "employee_id": emp.employee_id,
            "name": emp.name,
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "company_email": emp.company_email,
            "department": emp.department,
            "role": emp.role,
            "team": emp.team,
            "category": emp.category,
        }
        for emp in employees
    ]


@router.get("/{category}/skill-categories", response_model=List[str])
def get_skill_categories_for_employee_category(
    category: str,
    db: Session = Depends(database.get_db),
):
    """Get distinct skill categories for skills in a given employee category template."""
    skill_categories = (
        db.query(Skill.category)
        .join(CategorySkillTemplate, CategorySkillTemplate.skill_id == Skill.id)
        .filter(CategorySkillTemplate.category == category)
        .filter(Skill.category.isnot(None))
        .distinct()
        .all()
    )
    return [cat[0] for cat in skill_categories if cat[0]]


@router.get("/{category}/template-with-stats")
def get_category_template_with_stats(
    category: str,
    db: Session = Depends(database.get_db),
):
    """Get skill template for a category with rating distribution statistics."""
    from app.db.models import EmployeeSkill
    from sqlalchemy import func
    
    templates = (
        db.query(CategorySkillTemplate)
        .filter(CategorySkillTemplate.category == category)
        .order_by(CategorySkillTemplate.display_order.asc().nullslast(), CategorySkillTemplate.id.asc())
        .all()
    )
    
    result = []
    for template in templates:
        skill = db.query(Skill).filter(Skill.id == template.skill_id).first()
        
        # Get rating distribution for this skill
        rating_stats = (
            db.query(
                EmployeeSkill.rating,
                func.count(EmployeeSkill.id).label('count')
            )
            .join(Employee, Employee.id == EmployeeSkill.employee_id)
            .filter(
                EmployeeSkill.skill_id == template.skill_id,
                Employee.category == category,
                EmployeeSkill.rating.isnot(None)
            )
            .group_by(EmployeeSkill.rating)
            .all()
        )
        
        rating_breakdown = {
            "Beginner": 0,
            "Developing": 0,
            "Intermediate": 0,
            "Advanced": 0,
            "Expert": 0,
        }
        
        for rating, count in rating_stats:
            if rating in rating_breakdown:
                rating_breakdown[rating] = count
        
        total_employees = sum(rating_breakdown.values())
        
        result.append({
            "id": template.id,
            "category": template.category,
            "skill_id": template.skill_id,
            "is_required": template.is_required,
            "display_order": template.display_order,
            "skill": {
                "id": skill.id,
                "name": skill.name,
                "description": skill.description,
                "category": skill.category,
            } if skill else None,
            "rating_breakdown": rating_breakdown,
            "total_employees": total_employees,
        })
    
    return result

