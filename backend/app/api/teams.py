"""API routes for team management and team skill templates."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import database, crud
from app.db.models import TeamSkillTemplate, Skill, Employee
from app.api.dependencies import get_admin_user
from app.db.models import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/teams", tags=["teams"])

# Team constants
TEAMS = [
    "consulting",
    "technical_delivery",
    "project_programming",
    "corporate_functions_it",
    "corporate_functions_marketing",
    "corporate_functions_finance",
    "corporate_functions_legal",
    "corporate_functions_pc",
]

# Team display names
TEAM_DISPLAY_NAMES = {
    "consulting": "Consulting",
    "technical_delivery": "Technical Delivery",
    "project_programming": "Project Programming",
    "corporate_functions_it": "Corporate Functions - IT",
    "corporate_functions_marketing": "Corporate Functions - Marketing",
    "corporate_functions_finance": "Corporate Functions - Finance",
    "corporate_functions_legal": "Corporate Functions - Legal",
    "corporate_functions_pc": "Corporate Functions - P&C",
}


class TeamSkillTemplateCreate(BaseModel):
    team: str
    skill_id: int
    is_required: bool = False
    display_order: Optional[int] = None


class TeamSkillTemplateResponse(BaseModel):
    id: int
    team: str
    skill_id: int
    is_required: bool
    display_order: Optional[int]
    skill: dict

    class Config:
        from_attributes = True


@router.get("/", response_model=List[str])
def get_teams():
    """Get list of all available teams."""
    return TEAMS


@router.get("/display-names")
def get_team_display_names():
    """Get team display names mapping."""
    return TEAM_DISPLAY_NAMES


@router.get("/{team}/template", response_model=List[TeamSkillTemplateResponse])
def get_team_template(
    team: str,
    db: Session = Depends(database.get_db),
):
    """Get skill template for a specific team."""
    if team not in TEAMS:
        raise HTTPException(status_code=400, detail=f"Invalid team: {team}")
    
    templates = (
        db.query(TeamSkillTemplate)
        .filter(TeamSkillTemplate.team == team)
        .order_by(TeamSkillTemplate.display_order.asc().nullslast(), TeamSkillTemplate.id.asc())
        .all()
    )
    
    result = []
    for template in templates:
        skill = db.query(Skill).filter(Skill.id == template.skill_id).first()
        result.append({
            "id": template.id,
            "team": template.team,
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


@router.post("/{team}/template", response_model=TeamSkillTemplateResponse)
def create_team_template(
    team: str,
    template: TeamSkillTemplateCreate,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_admin_user),
):
    """Create a skill template entry for a team (admin only)."""
    if team not in TEAMS:
        raise HTTPException(status_code=400, detail=f"Invalid team: {team}")
    
    if template.team != team:
        raise HTTPException(status_code=400, detail="Team mismatch in URL and body")
    
    # Verify skill exists
    skill = db.query(Skill).filter(Skill.id == template.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # Check if template already exists
    existing = (
        db.query(TeamSkillTemplate)
        .filter(
            TeamSkillTemplate.team == team,
            TeamSkillTemplate.skill_id == template.skill_id
        )
        .first()
    )
    
    if existing:
        raise HTTPException(status_code=400, detail="Template entry already exists for this team and skill")
    
    # Create template
    db_template = TeamSkillTemplate(
        team=team,
        skill_id=template.skill_id,
        is_required=template.is_required,
        display_order=template.display_order,
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return {
        "id": db_template.id,
        "team": db_template.team,
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


@router.delete("/{team}/template/{template_id}")
def delete_team_template(
    team: str,
    template_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_admin_user),
):
    """Delete a skill template entry for a team (admin only)."""
    if team not in TEAMS:
        raise HTTPException(status_code=400, detail=f"Invalid team: {team}")
    
    template = (
        db.query(TeamSkillTemplate)
        .filter(
            TeamSkillTemplate.id == template_id,
            TeamSkillTemplate.team == team
        )
        .first()
    )
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(template)
    db.commit()
    
    return {"message": "Template deleted successfully"}


@router.get("/employees/by-team")
def get_employees_by_team(
    team: str = Query(..., description="Team name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(database.get_db),
):
    """Get employees by team."""
    if team not in TEAMS:
        raise HTTPException(status_code=400, detail=f"Invalid team: {team}")
    
    employees = (
        db.query(Employee)
        .filter(Employee.team == team)
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
        }
        for emp in employees
    ]

