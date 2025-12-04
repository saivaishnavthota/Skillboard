#!/usr/bin/env python3
"""Populate example role requirements for testing."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import Skill, RoleRequirement, RatingEnum
from sqlalchemy.exc import IntegrityError

def populate_requirements():
    """Populate example role requirements."""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("Populating Example Role Requirements")
        print("=" * 60)
        
        # Define example requirements
        # Format: (skill_name, band, required_rating)
        example_requirements = [
            # Programming Skills
            ("Python", "A", RatingEnum.BEGINNER),
            ("Python", "B", RatingEnum.INTERMEDIATE),
            ("Python", "C", RatingEnum.ADVANCED),
            ("Python", "L1", RatingEnum.ADVANCED),
            ("Python", "L2", RatingEnum.EXPERT),
            
            ("JavaScript", "A", RatingEnum.BEGINNER),
            ("JavaScript", "B", RatingEnum.INTERMEDIATE),
            ("JavaScript", "C", RatingEnum.ADVANCED),
            
            ("Java", "A", RatingEnum.BEGINNER),
            ("Java", "B", RatingEnum.INTERMEDIATE),
            ("Java", "C", RatingEnum.ADVANCED),
            
            # Cloud Skills
            ("AWS", "B", RatingEnum.BEGINNER),
            ("AWS", "C", RatingEnum.INTERMEDIATE),
            ("AWS", "L1", RatingEnum.ADVANCED),
            
            ("Azure", "B", RatingEnum.BEGINNER),
            ("Azure", "C", RatingEnum.INTERMEDIATE),
            
            # Database Skills
            ("SQL", "A", RatingEnum.BEGINNER),
            ("SQL", "B", RatingEnum.INTERMEDIATE),
            ("SQL", "C", RatingEnum.ADVANCED),
            
            # DevOps Skills
            ("Docker", "B", RatingEnum.BEGINNER),
            ("Docker", "C", RatingEnum.INTERMEDIATE),
            
            ("Kubernetes", "C", RatingEnum.BEGINNER),
            ("Kubernetes", "L1", RatingEnum.INTERMEDIATE),
            
            # Soft Skills
            ("Communication", "A", RatingEnum.INTERMEDIATE),
            ("Communication", "B", RatingEnum.INTERMEDIATE),
            ("Communication", "C", RatingEnum.ADVANCED),
            ("Communication", "L1", RatingEnum.ADVANCED),
            ("Communication", "L2", RatingEnum.EXPERT),
            
            ("Leadership", "C", RatingEnum.INTERMEDIATE),
            ("Leadership", "L1", RatingEnum.ADVANCED),
            ("Leadership", "L2", RatingEnum.EXPERT),
        ]
        
        added_count = 0
        skipped_count = 0
        error_count = 0
        
        for skill_name, band, required_rating in example_requirements:
            # Find skill
            skill = db.query(Skill).filter(Skill.name == skill_name).first()
            
            if not skill:
                print(f"⚠️  Skill '{skill_name}' not found - skipping")
                skipped_count += 1
                continue
            
            # Check if requirement already exists
            existing = db.query(RoleRequirement).filter(
                RoleRequirement.band == band,
                RoleRequirement.skill_id == skill.id
            ).first()
            
            if existing:
                print(f"⏭️  Band {band} - {skill_name} ({required_rating.value}) - already exists")
                skipped_count += 1
                continue
            
            # Create requirement
            try:
                requirement = RoleRequirement(
                    band=band,
                    skill_id=skill.id,
                    required_rating=required_rating,
                    is_required=True
                )
                db.add(requirement)
                db.commit()
                print(f"✓ Added: Band {band} - {skill_name} → {required_rating.value}")
                added_count += 1
            except IntegrityError as e:
                db.rollback()
                print(f"❌ Error adding Band {band} - {skill_name}: {e}")
                error_count += 1
        
        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)
        print(f"✓ Added: {added_count}")
        print(f"⏭️  Skipped: {skipped_count}")
        print(f"❌ Errors: {error_count}")
        
        if added_count > 0:
            print("\n✓ Example role requirements populated successfully!")
            print("\nNext steps:")
            print("1. Review requirements: GET /api/role-requirements")
            print("2. Create courses and map them to skills")
            print("3. Trigger auto-assignment: POST /api/learning/auto-assign-by-skill-gap")
        else:
            print("\n⚠️  No new requirements added.")
            print("This might be because:")
            print("- Requirements already exist")
            print("- Skills don't exist in your database")
            print("- You need to import skills first")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    populate_requirements()
