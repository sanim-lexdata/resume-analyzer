"""
Example: How to integrate the database into your Resume Analyzer app
Add this code to your main_enhanced.py or app.py
"""

from src.database import ResumeDatabase

class ResumeAnalyzerWithDB:
    """Enhanced Resume Analyzer with Database Support"""
    
    def __init__(self):
        # Initialize database
        self.db = ResumeDatabase()
        # ... your other initializations
    
    def analyze_resume_with_db(self, resume_path, job_description=None):
        """
        Analyze resume and save results to database.
        """
        # Step 1: Extract resume text
        resume_text = self.extract_text(resume_path)
        file_size = os.path.getsize(resume_path)
        file_type = resume_path.split('.')[-1]
        
        # Step 2: Save resume to database
        resume_id = self.db.insert_resume(
            filename=os.path.basename(resume_path),
            file_size=file_size,
            file_type=file_type,
            full_text=resume_text
        )
        print(f"Resume saved to database with ID: {resume_id}")
        
        # Step 3: Perform analysis (your existing code)
        analysis_result = self.perform_analysis(resume_text, job_description)
        
        # Step 4: Save job description if provided
        job_id = None
        if job_description:
            job_id = self.db.insert_job_description(
                title=job_description.get('title', 'N/A'),
                company=job_description.get('company', 'N/A'),
                description=job_description.get('description', ''),
                requirements=job_description.get('requirements', '')
            )
        
        # Step 5: Save analysis results to database
        analysis_id = self.db.insert_analysis_result(
            resume_id=resume_id,
            job_id=job_id,
            match_score=analysis_result.get('match_score', 0),
            ats_score=analysis_result.get('ats_score', 0),
            keyword_match_count=len(analysis_result.get('matched_keywords', [])),
            missing_keywords=analysis_result.get('missing_keywords', []),
            strengths=analysis_result.get('strengths', []),
            weaknesses=analysis_result.get('weaknesses', []),
            recommendations=analysis_result.get('recommendations', []),
            detailed_analysis=analysis_result
        )
        
        # Step 6: Save extracted skills
        if 'skills' in analysis_result:
            self.db.insert_skills(resume_id, analysis_result['skills'])
        
        # Step 7: Save contact information
        contact_info = analysis_result.get('contact_info', {})
        if contact_info:
            self.db.insert_contact_info(
                resume_id=resume_id,
                email=contact_info.get('email'),
                phone=contact_info.get('phone'),
                linkedin=contact_info.get('linkedin'),
                github=contact_info.get('github'),
                website=contact_info.get('website'),
                location=contact_info.get('location')
            )
        
        print(f"Analysis saved to database with ID: {analysis_id}")
        
        return {
            'resume_id': resume_id,
            'analysis_id': analysis_id,
            'results': analysis_result
        }
    
    def get_resume_history(self):
        """Get all previously analyzed resumes."""
        return self.db.get_all_resumes()
    
    def get_analysis_history(self, resume_id):
        """Get all analyses for a specific resume."""
        return self.db.get_analysis_results(resume_id)
    
    def view_statistics(self):
        """View database statistics."""
        stats = self.db.get_statistics()
        print("\n" + "="*50)
        print("RESUME ANALYZER STATISTICS")
        print("="*50)
        print(f"Total Resumes Analyzed: {stats['total_resumes']}")
        print(f"Total Job Descriptions: {stats['total_jobs']}")
        print(f"Total Analyses Performed: {stats['total_analyses']}")
        print(f"Average Match Score: {stats['average_match_score']}%")
        print("="*50 + "\n")
        return stats


# ============================================
# INTEGRATION WITH STREAMLIT APP
# ============================================

def integrate_with_streamlit():
    """
    Example: How to add database features to your Streamlit app
    Add these sections to your app.py
    """
    
    # In your app.py, add this to imports:
    # from src.database import ResumeDatabase
    
    # In your main() function or session state initialization:
    # if 'db' not in st.session_state:
    #     st.session_state.db = ResumeDatabase()
    
    # Add a sidebar menu for database features:
    """
    st.sidebar.title("Database")
    db_menu = st.sidebar.radio("Choose Option", [
        "Current Analysis",
        "Resume History", 
        "Statistics",
        "Manage Data"
    ])
    
    if db_menu == "Resume History":
        st.subheader("Previously Analyzed Resumes")
        resumes = st.session_state.db.get_all_resumes()
        
        if resumes:
            for resume in resumes:
                with st.expander(f"{resume['filename']} - {resume['upload_date']}"):
                    st.write(f"File Size: {resume['file_size']} bytes")
                    st.write(f"Resume ID: {resume['id']}")
                    
                    # Show analysis history for this resume
                    analyses = st.session_state.db.get_analysis_results(resume['id'])
                    if analyses:
                        st.write(f"Total Analyses: {len(analyses)}")
                        for analysis in analyses:
                            st.write(f"Match Score: {analysis['match_score']}%")
                            st.write(f"ATS Score: {analysis['ats_score']}%")
        else:
            st.info("No resumes in database yet.")
    
    elif db_menu == "Statistics":
        st.subheader("Database Statistics")
        stats = st.session_state.db.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Resumes", stats['total_resumes'])
        col2.metric("Total Jobs", stats['total_jobs'])
        col3.metric("Total Analyses", stats['total_analyses'])
        col4.metric("Avg Match Score", f"{stats['average_match_score']}%")
    """

# ============================================
# COMMAND LINE USAGE EXAMPLE
# ============================================

def command_line_example():
    """Example of using database from command line."""
    
    # Initialize database
    db = ResumeDatabase()
    
    # Add a resume
    resume_id = db.insert_resume(
        filename="my_resume.pdf",
        file_size=250000,
        file_type="pdf",
        full_text="Resume content here..."
    )
    
    # Add analysis result
    analysis_id = db.insert_analysis_result(
        resume_id=resume_id,
        job_id=None,
        match_score=88.5,
        ats_score=91.0,
        keyword_match_count=15,
        missing_keywords=["Docker", "AWS"],
        strengths=["Strong Python", "Good experience"],
        weaknesses=["Limited cloud knowledge"],
        recommendations=["Learn AWS", "Get certified"],
        detailed_analysis={"score": 88.5}
    )
    
    # Retrieve data
    resume = db.get_resume_by_id(resume_id)
    analyses = db.get_analysis_results(resume_id)
    
    print(f"Resume: {resume['filename']}")
    print(f"Analyses: {len(analyses)}")
    
    # Get statistics
    stats = db.get_statistics()
    print(f"Total resumes in database: {stats['total_resumes']}")

if __name__ == "__main__":
    print("This file contains integration examples.")
    print("See the code for how to integrate database into your app.")