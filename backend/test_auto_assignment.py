#!/usr/bin/env python3
"""Test script for learning auto-assignment feature."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.db.models import Employee, Skill, Course, RoleRequirement, EmployeeSkill, RatingEnum, CourseAssignment
from sqlalchemy import text

def test_auto_assignment():
    """Test the auto-assignment logic."""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("Testing Learning Auto-Assignment Feature")
        print("=" * 60)
        
        # 1. Check if we have employees
        employees = db.query(Employee).limit(5).all()
        print(f"\n✓ Found {len(employees)} employees (showing first 5)")
        for emp in employees:
            print(f"  - {emp.name} (Band: {emp.band or 'Not Set'})")
        
        # 2. Check if we have skills
        skills = db.query(Skill).limit(5).all()
        print(f"\n✓ Found {db.query(Skill).count()} skills (showing first 5)")
        for skill in skills:
            print(f"  - {skill.name} (Category: {skill.category or 'None'})")
        
        # 3. Check if we have courses
        courses = db.query(Course).all()
        print(f"\n✓ Found {len(courses)} courses")
        for course in courses:
            skill_name = "No skill mapping"
            if course.skill_id:
                skill = db.query(Skill).filter(Skill.id == course.skill_id).first()
                skill_name = f"Mapped to: {skill.name}" if skill else "Invalid skill mapping"
            print(f"  - {course.title} ({skill_name})")
        
        # 4. Check if we have role requirements
        requirements = db.query(RoleRequirement).all()
        print(f"\n✓ Found {len(requirements)} role requirements")
        if requirements:
            for req in requirements:
                skill = db.query(Skill).filter(Skill.id == req.skill_id).first()
                print(f"  - Band {req.band}: {skill.name if skill else 'Unknown'} → {req.required_rating.value}")
        else:
            print("  ⚠️  No role requirements defined yet!")
            print("  → Run: python migrations/apply_role_requirements.py")
            print("  → Then add requirements via API or database")
        
        # 5. Check for skill gaps
        print("\n" + "=" * 60)
        print("Analyzing Skill Gaps")
        print("=" * 60)
        
        gap_count = 0
        for emp in employees:
            if not emp.band:
                continue
            
            emp_requirements = db.query(RoleRequirement).filter(
                RoleRequirement.band == emp.band
            ).all()
            
            if not emp_requirements:
                continue
            
            emp_gaps = []
            for req in emp_requirements:
                emp_skill = db.query(EmployeeSkill).filter(
                    EmployeeSkill.employee_id == emp.id,
                    EmployeeSkill.skill_id == req.skill_id
                ).first()
                
                # Rating levels
                rating_levels = {
                    None: 0,
                    RatingEnum.BEGINNER: 1,
                    RatingEnum.DEVELOPING: 2,
                    RatingEnum.INTERMEDIATE: 3,
                    RatingEnum.ADVANCED: 4,
                    RatingEnum.EXPERT: 5,
                }
                
                current_level = rating_levels.get(emp_skill.rating if emp_skill else None, 0)
                required_level = rating_levels.get(req.required_rating, 0)
                
                if current_level < required_level:
                    skill = db.query(Skill).filter(Skill.id == req.skill_id).first()
                    current_rating = emp_skill.rating.value if emp_skill and emp_skill.rating else "None"
                    emp_gaps.append({
                        'skill': skill.name if skill else 'Unknown',
                        'current': current_rating,
                        'required': req.required_rating.value
                    })
            
            if emp_gaps:
                gap_count += 1
                print(f"\n{emp.name} (Band {emp.band}):")
                for gap in emp_gaps:
                    print(f"  ⚠️  {gap['skill']}: {gap['current']} → {gap['required']}")
                    
                    # Check available courses
                    skill = db.query(Skill).filter(Skill.name == gap['skill']).first()
                    if skill:
                        available_courses = db.query(Course).filter(Course.skill_id == skill.id).all()
                        if available_courses:
                            print(f"     Available courses: {', '.join([c.title for c in available_courses])}")
                        else:
                            print(f"     ⚠️  No courses available for this skill")
        
        if gap_count == 0:
            print("\n✓ No skill gaps found! All employees meet their band requirements.")
        else:
            print(f"\n✓ Found skill gaps for {gap_count} employee(s)")
        
        # 6. Check existing assignments
        assignments = db.query(CourseAssignment).all()
        print(f"\n✓ Found {len(assignments)} existing course assignments")
        
        print("\n" + "=" * 60)
        print("Test Complete!")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Ensure role requirements are defined for your bands")
        print("2. Create courses and map them to skills")
        print("3. Use the admin panel to trigger auto-assignment")
        print("4. Or use API: POST /api/learning/auto-assign-by-skill-gap")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_auto_assignment()
