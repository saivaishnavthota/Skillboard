"""CRUD operations for database models."""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.db.models import Skill, Employee, EmployeeSkill, RatingEnum, User


# Skill CRUD
def get_skill_by_name(db: Session, name: str) -> Optional[Skill]:
    """Get skill by name."""
    return db.query(Skill).filter(Skill.name == name).first()


def get_skill_by_id(db: Session, skill_id: int) -> Optional[Skill]:
    """Get skill by ID."""
    return db.query(Skill).filter(Skill.id == skill_id).first()


def get_all_skills(db: Session, skip: int = 0, limit: int = 100) -> List[Skill]:
    """Get all skills with pagination."""
    return db.query(Skill).offset(skip).limit(limit).all()


def create_skill(db: Session, skill: dict) -> Skill:
    """Create a new skill."""
    db_skill = Skill(**skill)
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill


def upsert_skill(db: Session, name: str, description: Optional[str] = None, category: Optional[str] = None) -> Skill:
    """Create or update a skill."""
    db_skill = get_skill_by_name(db, name)
    if db_skill:
        # Update description if provided
        if description is not None:
            db_skill.description = description
        # Update category if provided (including empty string to clear it)
        if category is not None:
            db_skill.category = category if category.strip() else None
        # Commit if any updates were made
        if description is not None or category is not None:
            db.commit()
            db.refresh(db_skill)
        return db_skill
    else:
        # Create new skill with category (empty string becomes None)
        final_category = category.strip() if category and category.strip() else None
        return create_skill(db, {"name": name, "description": description, "category": final_category})


# Employee CRUD
def get_employee_by_id(db: Session, employee_id: str) -> Optional[Employee]:
    """Get employee by employee_id (string ID)."""
    return db.query(Employee).filter(Employee.employee_id == employee_id).first()


def get_employee_by_db_id(db: Session, db_id: int) -> Optional[Employee]:
    """Get employee by database ID."""
    return db.query(Employee).filter(Employee.id == db_id).first()


def create_employee(db: Session, employee: dict) -> Employee:
    """Create a new employee."""
    db_employee = Employee(**employee)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def upsert_employee(
    db: Session,
    employee_id: str,
    name: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    company_email: Optional[str] = None,
    department: Optional[str] = None,
    role: Optional[str] = None,
    team: Optional[str] = None,
    category: Optional[str] = None,
) -> Employee:
    """Create or update an employee."""
    db_employee = get_employee_by_id(db, employee_id)
    if db_employee:
        db_employee.name = name
        if first_name is not None:
            db_employee.first_name = first_name
        if last_name is not None:
            db_employee.last_name = last_name
        if company_email is not None:
            db_employee.company_email = company_email
        if department is not None:
            db_employee.department = department
        if role is not None:
            db_employee.role = role
        if team is not None:
            db_employee.team = team
        if category is not None:
            db_employee.category = category
        db.commit()
        db.refresh(db_employee)
        return db_employee
    else:
        return create_employee(
            db,
            {
                "employee_id": employee_id,
                "name": name,
                "first_name": first_name,
                "last_name": last_name,
                "company_email": company_email,
                "department": department,
                "role": role,
                "team": team,
                "category": category,
            },
        )


# EmployeeSkill CRUD
def get_employee_skill(
    db: Session, employee_id: int, skill_id: int
) -> Optional[EmployeeSkill]:
    """Get employee-skill mapping."""
    return (
        db.query(EmployeeSkill)
        .filter(
            EmployeeSkill.employee_id == employee_id,
            EmployeeSkill.skill_id == skill_id,
        )
        .first()
    )


def create_employee_skill(db: Session, employee_skill: dict) -> EmployeeSkill:
    """Create a new employee-skill mapping."""
    # Set initial_rating to the first rating if not already set
    if "rating" in employee_skill and employee_skill["rating"] and "initial_rating" not in employee_skill:
        employee_skill["initial_rating"] = employee_skill["rating"]
    
    db_employee_skill = EmployeeSkill(**employee_skill)
    db.add(db_employee_skill)
    db.commit()
    db.refresh(db_employee_skill)
    return db_employee_skill


def upsert_employee_skill(
    db: Session,
    employee_id: int,
    skill_id: int,
    rating: Optional[RatingEnum] = None,
    years_experience: Optional[float] = None,
    is_interested: bool = False,
    notes: Optional[str] = None,
    match_score: Optional[float] = None,
    needs_review: bool = False,
    is_custom: bool = False,
) -> EmployeeSkill:
    """Create or update an employee-skill mapping."""
    db_employee_skill = get_employee_skill(db, employee_id, skill_id)
    if db_employee_skill:
        # Only update rating if provided and not an interested skill
        if rating is not None and not is_interested:
            # Convert enum to value (string) for storage
            rating_value = rating.value if hasattr(rating, 'value') else str(rating)
            # Set initial_rating if it's not set yet (first time setting a rating)
            if db_employee_skill.initial_rating is None:
                db_employee_skill.initial_rating = rating_value
            db_employee_skill.rating = rating_value
        elif is_interested:
            # Clear rating for interested skills
            db_employee_skill.rating = None
        if years_experience is not None:
            db_employee_skill.years_experience = years_experience
        if is_interested is not None:
            db_employee_skill.is_interested = is_interested
        if notes is not None:
            db_employee_skill.notes = notes
        if match_score is not None:
            db_employee_skill.match_score = match_score
        db_employee_skill.needs_review = needs_review
        db_employee_skill.is_custom = is_custom
        db.commit()
        db.refresh(db_employee_skill)
        return db_employee_skill
    else:
        # For interested skills, rating should be None
        final_rating = None if is_interested else (rating or RatingEnum.BEGINNER)
        # Convert enum to value (string) for storage
        final_rating_value = final_rating.value if final_rating and hasattr(final_rating, 'value') else (str(final_rating) if final_rating else None)
        initial_rating_value = final_rating_value if final_rating_value else None
        return create_employee_skill(
            db,
            {
                "employee_id": employee_id,
                "skill_id": skill_id,
                "rating": final_rating_value,
                "initial_rating": initial_rating_value,
                "years_experience": years_experience,
                "is_interested": is_interested,
                "notes": notes,
                "match_score": match_score,
                "needs_review": needs_review,
                "is_custom": is_custom,
            },
        )


def get_employee_skills_by_employee_id(
    db: Session, employee_id: int
) -> List[EmployeeSkill]:
    """Get all skills for an employee."""
    return (
        db.query(EmployeeSkill)
        .filter(EmployeeSkill.employee_id == employee_id)
        .all()
    )


def get_all_employee_skills(db: Session) -> List[EmployeeSkill]:
    """Get all employee-skill mappings."""
    return db.query(EmployeeSkill).all()


def search_employees_by_skill_names(
    db: Session, skill_names: List[str]
) -> List[Employee]:
    """Get employees who have any of the given skills."""
    return (
        db.query(Employee)
        .join(EmployeeSkill)
        .join(Skill)
        .filter(Skill.name.in_(skill_names))
        .distinct()
        .all()
    )


# User CRUD
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_employee_id(db: Session, employee_id: str) -> Optional[User]:
    """Get user by employee_id."""
    return db.query(User).filter(User.employee_id == employee_id).first()


def create_user(db: Session, user: dict) -> User:
    """Create a new user."""
    db_user = User(**user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_data: dict) -> Optional[User]:
    """Update a user."""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    for key, value in user_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

