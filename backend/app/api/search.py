"""API routes for fuzzy search functionality."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.db import database, crud
from app.schemas import FuzzySearchResult, MatchedSkillInfo
from rapidfuzz import process, fuzz
from collections import defaultdict

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/skills", response_model=List[FuzzySearchResult])
def fuzzy_search_skills(
    q: str = Query(..., description="Search query for skill name"),
    threshold: int = Query(75, ge=0, le=100, description="Minimum match score (0-100)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(database.get_db),
):
    """
    Fuzzy search for employees by skill name.
    Returns employees who have skills matching the query.
    """
    if not q or not q.strip():
        return []

    query = q.strip().lower()

    # Get all skills from database
    all_skills = crud.get_all_skills(db, skip=0, limit=10000)
    skill_names = [skill.name for skill in all_skills]

    if not skill_names:
        return []

    # Use RapidFuzz to find matching skills
    # Using token_sort_ratio for better matching of skill names
    matches = process.extract(
        query,
        skill_names,
        scorer=fuzz.token_sort_ratio,
        limit=limit * 2,  # Get more matches to filter by threshold
    )

    # Filter by threshold and extract matched skill names
    matched_skill_names = [
        skill_name for skill_name, score, _ in matches if score >= threshold
    ]

    if not matched_skill_names:
        return []

    # Get all employee skills that match these skill names
    from app.db.models import Employee, EmployeeSkill, Skill

    employee_skills_query = (
        db.query(Employee, EmployeeSkill, Skill)
        .join(EmployeeSkill, Employee.id == EmployeeSkill.employee_id)
        .join(Skill, EmployeeSkill.skill_id == Skill.id)
        .filter(Skill.name.in_(matched_skill_names))
        .all()
    )

    # Group by employee and collect matched skills with scores
    employee_results = defaultdict(lambda: {
        "employee": None,
        "matched_skills": [],
        "all_skills": []
    })

    # Create a map of skill name to match score
    skill_score_map = {skill_name: score for skill_name, score, _ in matches}

    for employee, employee_skill, skill in employee_skills_query:
        emp_id = employee.employee_id
        if employee_results[emp_id]["employee"] is None:
            employee_results[emp_id]["employee"] = employee

        # Add matched skill info
        match_score = skill_score_map.get(skill.name, 0)
        employee_results[emp_id]["matched_skills"].append({
            "skill_name": skill.name,
            "match_score": match_score
        })

        # Add all skills for this employee (for ratings display)
        employee_results[emp_id]["all_skills"].append({
            "skill_name": skill.name,
            "rating": employee_skill.rating.value,
            "years_experience": employee_skill.years_experience
        })

    # Build response
    results = []
    for emp_id, data in employee_results.items():
        employee = data["employee"]
        matched_skills = data["matched_skills"]
        
        # Calculate overall match score (average of top matches)
        if matched_skills:
            scores = [m["match_score"] for m in matched_skills]
            overall_score = max(scores)  # Use max score for overall
        else:
            overall_score = 0

        # Remove duplicates from matched_skills
        seen = set()
        unique_matched = []
        for m in matched_skills:
            if m["skill_name"] not in seen:
                seen.add(m["skill_name"])
                unique_matched.append(MatchedSkillInfo(**m))

        results.append(
            FuzzySearchResult(
                employee_id=employee.employee_id,
                employee_name=employee.name,
                overall_match_score=round(overall_score, 2),
                matched_skills=unique_matched,
                ratings=data["all_skills"]
            )
        )

    # Sort by overall match score (descending) and limit
    results.sort(key=lambda x: x.overall_match_score, reverse=True)
    return results[:limit]

