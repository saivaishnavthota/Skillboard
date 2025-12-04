"""Create learning platform tables in the database."""
from app.db.database import engine
from app.db.models import Base, Course, CourseAssignment

def create_tables():
    """Create all tables defined in models."""
    print("Creating learning platform tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully!")

if __name__ == "__main__":
    create_tables()
