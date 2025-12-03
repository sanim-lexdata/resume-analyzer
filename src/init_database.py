"""
Database Initialization Script for Resume Analyzer
Run this file to create the database and tables.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import ResumeDatabase

def initialize_database():
    """Initialize the database with all tables."""
    print("=" * 60)
    print("Resume Analyzer - Database Initialization")
    print("=" * 60)
    print()
    
    try:
        # Create database instance
        print("Creating database...")
        db = ResumeDatabase()
        print("Database created successfully!")
        print(f"Location: {db.db_path}")
        print()
        
        # Get statistics
        print("Database Statistics:")
        stats = db.get_statistics()
        print(f"  - Total Resumes: {stats['total_resumes']}")
        print(f"  - Total Job Descriptions: {stats['total_jobs']}")
        print(f"  - Total Analyses: {stats['total_analyses']}")
        print(f"  - Average Match Score: {stats['average_match_score']}%")
        print()
        
        print("=" * 60)
        print("Database initialized successfully!")
        print("=" * 60)
        
        return db
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def add_sample_data(db):
    """Add sample data to test the database."""
    print()
    print("Adding sample data...")
    
    # Sample resume
    resume_id = db.insert_resume(
        filename="john_doe_resume.pdf",
        file_size=245000,
        file_type="pdf",
        full_text="John Doe\nSoftware Engineer\nPython, JavaScript, SQL..."
    )
    print(f"Sample resume added with ID: {resume_id}")
    
    # Sample job description
    job_id = db.insert_job_description(
        title="Senior Software Engineer",
        company="Tech Corp",
        description="Looking for an experienced software engineer...",
        requirements="Python, JavaScript, 5+ years experience"
    )
    print(f"Sample job description added with ID: {job_id}")
    
    # Sample analysis result
    analysis_id = db.insert_analysis_result(
        resume_id=resume_id,
        job_id=job_id,
        match_score=85.5,
        ats_score=92.0,
        keyword_match_count=12,
        missing_keywords=["Docker", "Kubernetes"],
        strengths=["Strong Python skills", "Good experience"],
        weaknesses=["Missing cloud experience"],
        recommendations=["Add cloud certifications", "Include Docker projects"],
        detailed_analysis={"sections": ["summary", "experience", "skills"]}
    )
    print(f"Sample analysis added with ID: {analysis_id}")
    
    # Sample skills
    skills = [
        {"name": "Python", "category": "Programming", "confidence": 0.95},
        {"name": "JavaScript", "category": "Programming", "confidence": 0.88},
        {"name": "SQL", "category": "Database", "confidence": 0.82}
    ]
    db.insert_skills(resume_id, skills)
    print(f"Sample skills added: {len(skills)} skills")
    
    # Sample contact info
    db.insert_contact_info(
        resume_id=resume_id,
        email="john.doe@email.com",
        phone="+1-555-0123",
        linkedin="linkedin.com/in/johndoe",
        github="github.com/johndoe",
        location="San Francisco, CA"
    )
    print("Sample contact information added")
    
    print()
    print("Sample data added successfully!")

if __name__ == "__main__":
    # Initialize database
    db = initialize_database()
    
    if db:
        # Ask if user wants to add sample data
        response = input("\nDo you want to add sample data for testing? (yes/no): ").lower()
        if response in ['yes', 'y']:
            add_sample_data(db)
        
        print("\nDatabase is ready to use!")
        print(f"Database file: {db.db_path}")