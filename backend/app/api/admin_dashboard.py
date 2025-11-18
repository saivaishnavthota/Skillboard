"""API routes for admin/HR dashboard."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import database, crud
from app.schemas import Employee, EmployeeSkill, Skill
from app.api.dependencies import get_admin_user
from app.db.models import User, Employee as EmployeeModel, EmployeeSkill as EmployeeSkillModel, Skill as SkillModel

router = APIRouter(prefix="/api/admin", tags=["admin-dashboard"])


@router.get("/employees", response_model=List[Employee])
def get_all_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    department: Optional[str] = Query(None),
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_admin_user),
):
    """Get all employees (admin/HR only)."""
    query = db.query(EmployeeModel)
    
    if department:
        query = query.filter(EmployeeModel.department == department)
    
    employees = query.offset(skip).limit(limit).all()
    return employees


@router.get("/employees/{employee_id}/skills", response_model=List[EmployeeSkill])
def get_employee_skills_admin(
    employee_id: str,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_admin_user),
):
    """Get all skills for a specific employee (admin/HR only)."""
    employee = crud.get_employee_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return crud.get_employee_skills_by_employee_id(db, employee.id)


@router.get("/skills/overview")
def get_skills_overview(
    category: Optional[str] = Query(None, description="Filter by employee category (e.g., Technical, P&C)"),
    skill_category: Optional[str] = Query(None, description="Filter by skill category (e.g., Programming, Database)"),
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_admin_user),
):
    """Get overview of all skills with employee counts and rating breakdown.
    
    If category is provided, only returns skills from that category's template.
    If skill_category is provided, filters by skill's category field.
    """
    from sqlalchemy import func, Integer, case, cast
    from app.db.models import RatingEnum, CategorySkillTemplate
    
    # Start with skills query
    skills_subquery = db.query(SkillModel)
    
    # If employee category filter is provided, only get skills from that category template
    if category:
        skills_subquery = skills_subquery.join(
            CategorySkillTemplate, 
            CategorySkillTemplate.skill_id == SkillModel.id
        ).filter(CategorySkillTemplate.category == category)
    
    # If skill category filter is provided, filter by skill's category field
    if skill_category:
        skills_subquery = skills_subquery.filter(SkillModel.category == skill_category)
    
    # Get skill IDs from filtered skills
    skill_ids = [s.id for s in skills_subquery.all()]
    
    if not skill_ids:
        # No skills match the filters
        return []
    
    # Build base query with counts
    base_query = (
        db.query(
            SkillModel,
            func.count(func.distinct(EmployeeSkillModel.employee_id)).label('employee_count'),
            func.sum(cast(EmployeeSkillModel.is_interested == False, Integer)).label('existing_count'),
            func.sum(cast(EmployeeSkillModel.is_interested == True, Integer)).label('interested_count'),
        )
        .filter(SkillModel.id.in_(skill_ids))
        .outerjoin(EmployeeSkillModel, SkillModel.id == EmployeeSkillModel.skill_id)
    )
    
    # Get all skills with counts of employees who have them
    skills_with_counts = (
        base_query
        .group_by(SkillModel.id)
        .all()
    )
    
    result = []
    for skill, emp_count, existing_count, interested_count in skills_with_counts:
        # Get rating breakdown for this skill (only for existing skills, not interested)
        rating_breakdown = (
            db.query(
                EmployeeSkillModel.rating,
                func.count(EmployeeSkillModel.id).label('count')
            )
            .filter(EmployeeSkillModel.skill_id == skill.id)
            .filter(EmployeeSkillModel.is_interested == False)
            .filter(EmployeeSkillModel.rating.isnot(None))
            .group_by(EmployeeSkillModel.rating)
            .all()
        )
        
        # Build rating counts dictionary
        rating_counts = {
            "Beginner": 0,
            "Developing": 0,
            "Intermediate": 0,
            "Advanced": 0,
            "Expert": 0,
        }
        for rating, count in rating_breakdown:
            if rating:
                rating_counts[rating.value] = count
        
        result.append({
            "skill": {
                "id": skill.id,
                "name": skill.name,
                "description": skill.description,
                "category": skill.category,
            },
            "total_employees": emp_count or 0,
            "existing_skills_count": existing_count or 0,
            "interested_skills_count": interested_count or 0,
            "rating_breakdown": rating_counts,
        })
    
    return result


@router.get("/skill-improvements")
def get_skill_improvements(
    skill_id: Optional[int] = Query(None),
    employee_id: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_admin_user),
):
    """
    Get skill improvements - employees who have upgraded their skill ratings.
    Only shows skills where current_rating > initial_rating (actual improvements).
    """
    from app.db.models import RatingEnum
    
    # Rating order for comparison: Beginner < Developing < Intermediate < Advanced < Expert
    rating_order = {
        RatingEnum.BEGINNER: 1,
        RatingEnum.DEVELOPING: 2,
        RatingEnum.INTERMEDIATE: 3,
        RatingEnum.ADVANCED: 4,
        RatingEnum.EXPERT: 5,
    }
    
    # Get employees with their skill ratings
    query = (
        db.query(
            EmployeeModel.employee_id,
            EmployeeModel.name,
            SkillModel.name.label('skill_name'),
            EmployeeSkillModel.rating,
            EmployeeSkillModel.initial_rating,
            EmployeeSkillModel.years_experience,
            EmployeeSkillModel.is_interested,
        )
        .join(EmployeeSkillModel, EmployeeModel.id == EmployeeSkillModel.employee_id)
        .join(SkillModel, EmployeeSkillModel.skill_id == SkillModel.id)
        .filter(EmployeeSkillModel.is_interested == False)  # Only existing skills have ratings
        .filter(EmployeeSkillModel.rating.isnot(None))  # Only skills with ratings
        .filter(EmployeeSkillModel.initial_rating.isnot(None))  # Must have initial rating to compare
    )
    
    if skill_id:
        query = query.filter(SkillModel.id == skill_id)
    
    if employee_id:
        query = query.filter(EmployeeModel.employee_id == employee_id)
    
    results = query.all()
    
    improvements = []
    for row in results:
        current_rating = row.rating
        initial_rating = row.initial_rating
        
        # Only include if current rating is higher than initial rating
        if current_rating and initial_rating:
            current_order = rating_order.get(current_rating, 0)
            initial_order = rating_order.get(initial_rating, 0)
            
            if current_order > initial_order:
                improvements.append({
                    "employee_id": row.employee_id,
                    "employee_name": row.name,
                    "skill_name": row.skill_name,
                    "initial_rating": initial_rating.value,
                    "current_rating": current_rating.value,
                    "years_experience": row.years_experience,
                })
    
    return {
        "improvements": improvements,
        "total_count": len(improvements),
        "note": "Showing only skills where employees have improved (current rating > initial rating)."
    }


@router.get("/dashboard/stats")
def get_dashboard_stats(
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_admin_user),
):
    """Get dashboard statistics for admin/HR."""
    from sqlalchemy import func
    
    # Total employees
    total_employees = db.query(func.count(EmployeeModel.id)).scalar()
    
    # Total skills
    total_skills = db.query(func.count(SkillModel.id)).scalar()
    
    # Total employee-skill mappings
    total_mappings = db.query(func.count(EmployeeSkillModel.id)).scalar()
    
    # Employees with existing skills
    employees_with_skills = (
        db.query(func.count(func.distinct(EmployeeSkillModel.employee_id)))
        .filter(EmployeeSkillModel.is_interested == False)
        .scalar()
    )
    
    # Employees with interested skills
    employees_interested = (
        db.query(func.count(func.distinct(EmployeeSkillModel.employee_id)))
        .filter(EmployeeSkillModel.is_interested == True)
        .scalar()
    )
    
    # Skills by rating
    rating_counts = (
        db.query(
            EmployeeSkillModel.rating,
            func.count(EmployeeSkillModel.id).label('count')
        )
        .filter(EmployeeSkillModel.is_interested == False)
        .filter(EmployeeSkillModel.rating.isnot(None))
        .group_by(EmployeeSkillModel.rating)
        .all()
    )
    
    rating_breakdown = {}
    for rating, count in rating_counts:
        if rating:
            rating_breakdown[rating.value] = count
        else:
            rating_breakdown["None"] = count
    
    return {
        "total_employees": total_employees or 0,
        "total_skills": total_skills or 0,
        "total_skill_mappings": total_mappings or 0,
        "employees_with_existing_skills": employees_with_skills or 0,
        "employees_with_interested_skills": employees_interested or 0,
        "rating_breakdown": rating_breakdown,
    }

