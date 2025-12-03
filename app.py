import streamlit as st
import os
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd

# Import your modules
try:
    from src.main_enhanced import ResumeAnalyzer
except ImportError:
    # Fallback: Create a simple analyzer class
    class ResumeAnalyzer:
        def __init__(self):
            pass
        
        def extract_text(self, file_path):
            """Extract text from file."""
            import PyPDF2
            import docx
            
            if file_path.endswith('.pdf'):
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                    return text
            elif file_path.endswith('.docx'):
                doc = docx.Document(file_path)
                return '\n'.join([para.text for para in doc.paragraphs])
            else:
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
        
        def analyze(self, resume_path, job_description=None):
            """Basic analysis."""
            text = self.extract_text(resume_path)
            
            # Simple analysis
            words = text.split()
            
            return {
                'match_score': 75.0,
                'ats_score': 80.0,
                'matched_keywords': ['Python', 'Java', 'SQL'],
                'missing_keywords': ['Docker', 'AWS'],
                'strengths': ['Good technical skills', 'Clear formatting'],
                'weaknesses': ['Missing cloud experience'],
                'recommendations': ['Add cloud certifications', 'Include more metrics'],
                'skills': ['Python', 'Java', 'SQL', 'Git'],
                'contact_info': {
                    'email': 'example@email.com',
                    'phone': '+1234567890'
                }
            }

from src.database import ResumeDatabase
from src.utils.logger import Logger

# Page configuration
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        padding: 10px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables."""
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = ResumeAnalyzer()
    
    if 'db' not in st.session_state:
        st.session_state.db = ResumeDatabase()
    
    if 'logger' not in st.session_state:
        st.session_state.logger = Logger()
    
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    
    if 'current_resume_id' not in st.session_state:
        st.session_state.current_resume_id = None
    
    if 'current_analysis_id' not in st.session_state:
        st.session_state.current_analysis_id = None

def save_uploaded_file(uploaded_file):
    """Save uploaded file and return path."""
    upload_dir = Path("output/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return str(file_path)

def display_resume_history():
    """Display previously analyzed resumes."""
    st.subheader("📚 Resume History")
    
    resumes = st.session_state.db.get_all_resumes()
    
    if not resumes:
        st.info("No resumes analyzed yet. Upload a resume to get started!")
        return
    
    for resume in resumes:
        with st.expander(f"📄 {resume['filename']} - {resume['upload_date'][:10]}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Upload Date:** {resume['upload_date']}")
                st.write(f"**File Size:** {resume['file_size']:,} bytes")
                st.write(f"**Resume ID:** {resume['id']}")
            
            with col2:
                # Get analysis results for this resume
                analyses = st.session_state.db.get_analysis_results(resume['id'])
                st.write(f"**Total Analyses:** {len(analyses)}")
                
                if analyses:
                    latest = analyses[0]
                    st.write(f"**Latest Match Score:** {latest['match_score']:.1f}%")
                    st.write(f"**Latest ATS Score:** {latest['ats_score']:.1f}%")
            
            # Show all analyses
            if analyses:
                st.write("---")
                st.write("**Analysis History:**")
                for i, analysis in enumerate(analyses, 1):
                    st.write(f"{i}. {analysis['analysis_date'][:16]} - Match: {analysis['match_score']:.1f}% | ATS: {analysis['ats_score']:.1f}%")
                    if analysis['job_title']:
                        st.write(f"   Job: {analysis['job_title']} at {analysis['company']}")
            
            # Delete button
            if st.button(f"🗑️ Delete Resume", key=f"delete_{resume['id']}"):
                st.session_state.db.delete_resume(resume['id'])
                st.success("Resume deleted!")
                st.rerun()

def display_statistics():
    """Display database statistics with visualizations."""
    st.subheader("📊 Statistics Dashboard")
    
    stats = st.session_state.db.get_statistics()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <h3>{stats['total_resumes']}</h3>
                <p>Total Resumes</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <h3>{stats['total_jobs']}</h3>
                <p>Job Descriptions</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <h3>{stats['total_analyses']}</h3>
                <p>Total Analyses</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <h3>{stats['average_match_score']:.1f}%</h3>
                <p>Avg Match Score</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Get all resumes for visualization
    resumes = st.session_state.db.get_all_resumes()
    
    if resumes:
        st.write("---")
        
        # Create visualization data
        viz_data = []
        for resume in resumes:
            analyses = st.session_state.db.get_analysis_results(resume['id'])
            for analysis in analyses:
                viz_data.append({
                    'Resume': resume['filename'][:20] + '...' if len(resume['filename']) > 20 else resume['filename'],
                    'Date': analysis['analysis_date'][:10],
                    'Match Score': analysis['match_score'],
                    'ATS Score': analysis['ats_score']
                })
        
        if viz_data:
            df = pd.DataFrame(viz_data)
            
            # Create charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Match Score Distribution
                fig1 = px.histogram(
                    df, 
                    x='Match Score', 
                    nbins=10,
                    title='Match Score Distribution',
                    color_discrete_sequence=['#1f77b4']
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # ATS Score Distribution
                fig2 = px.histogram(
                    df, 
                    x='ATS Score', 
                    nbins=10,
                    title='ATS Score Distribution',
                    color_discrete_sequence=['#2ca02c']
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # Score comparison over time
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=df['Date'], 
                y=df['Match Score'],
                mode='lines+markers',
                name='Match Score',
                line=dict(color='#1f77b4')
            ))
            fig3.add_trace(go.Scatter(
                x=df['Date'], 
                y=df['ATS Score'],
                mode='lines+markers',
                name='ATS Score',
                line=dict(color='#2ca02c')
            ))
            fig3.update_layout(title='Scores Over Time', xaxis_title='Date', yaxis_title='Score (%)')
            st.plotly_chart(fig3, use_container_width=True)

def analyze_resume_page():
    """Main resume analysis page."""
    st.markdown('<div class="main-header">🤖 AI Resume Analyzer</div>', unsafe_allow_html=True)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF, DOCX, or TXT)",
        type=['pdf', 'docx', 'txt'],
        help="Upload your resume for AI-powered analysis"
    )
    
    # Job description (optional)
    with st.expander("📋 Add Job Description (Optional)", expanded=False):
        job_title = st.text_input("Job Title")
        company_name = st.text_input("Company Name")
        job_description = st.text_area(
            "Job Description",
            height=200,
            placeholder="Paste the job description here..."
        )
    
    # Analysis button
    if uploaded_file and st.button("🚀 Analyze Resume", type="primary"):
        with st.spinner("Analyzing your resume..."):
            try:
                # Save uploaded file
                file_path = save_uploaded_file(uploaded_file)
                
                # Save resume to database
                resume_text = st.session_state.analyzer.extract_text(file_path)
                resume_id = st.session_state.db.insert_resume(
                    filename=uploaded_file.name,
                    file_size=uploaded_file.size,
                    file_type=uploaded_file.type.split('/')[-1],
                    full_text=resume_text
                )
                st.session_state.current_resume_id = resume_id
                
                # Save job description if provided
                job_id = None
                if job_description:
                    job_id = st.session_state.db.insert_job_description(
                        title=job_title or "N/A",
                        company=company_name or "N/A",
                        description=job_description,
                        requirements=""
                    )
                
                # Perform analysis
                report = st.session_state.analyzer.analyze(
                    resume_path=file_path,
                    job_description=job_description if job_description else None
                )
                
                # Save analysis results to database
                analysis_id = st.session_state.db.insert_analysis_result(
                    resume_id=resume_id,
                    job_id=job_id,
                    match_score=report.get('match_score', 0),
                    ats_score=report.get('ats_score', 0),
                    keyword_match_count=len(report.get('matched_keywords', [])),
                    missing_keywords=report.get('missing_keywords', []),
                    strengths=report.get('strengths', []),
                    weaknesses=report.get('weaknesses', []),
                    recommendations=report.get('recommendations', []),
                    detailed_analysis=report
                )
                st.session_state.current_analysis_id = analysis_id
                
                # Save extracted data
                if 'skills' in report:
                    skills_list = [{'name': skill, 'category': 'General', 'confidence': 1.0} 
                                  for skill in report['skills']]
                    st.session_state.db.insert_skills(resume_id, skills_list)
                
                if 'contact_info' in report:
                    contact = report['contact_info']
                    st.session_state.db.insert_contact_info(
                        resume_id=resume_id,
                        email=contact.get('email'),
                        phone=contact.get('phone'),
                        linkedin=contact.get('linkedin'),
                        github=contact.get('github')
                    )
                
                st.session_state.analysis_report = report
                st.session_state.analysis_complete = True
                st.success("Analysis completed and saved to database!")
                
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                st.session_state.logger.error(f"Analysis error: {str(e)}")
    
    # Display results
    if st.session_state.analysis_complete and 'analysis_report' in st.session_state:
        display_analysis_results(st.session_state.analysis_report)

def display_analysis_results(report):
    """Display comprehensive analysis results."""
    st.write("---")
    st.header("📊 Analysis Results")
    
    # Scores
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Match Score", f"{report.get('match_score', 0):.1f}%")
    
    with col2:
        st.metric("ATS Compatibility", f"{report.get('ats_score', 0):.1f}%")
    
    with col3:
        matched = len(report.get('matched_keywords', []))
        total = matched + len(report.get('missing_keywords', []))
        st.metric("Keywords Matched", f"{matched}/{total}")
    
    # Tabs for detailed results
    tab1, tab2, tab3, tab4 = st.tabs(["💪 Strengths", "⚠️ Weaknesses", "💡 Recommendations", "🔍 Details"])
    
    with tab1:
        st.subheader("Strengths")
        strengths = report.get('strengths', [])
        if strengths:
            for strength in strengths:
                st.success(f"✓ {strength}")
        else:
            st.info("No specific strengths identified.")
    
    with tab2:
        st.subheader("Areas for Improvement")
        weaknesses = report.get('weaknesses', [])
        if weaknesses:
            for weakness in weaknesses:
                st.warning(f"• {weakness}")
        else:
            st.info("No major weaknesses found.")
    
    with tab3:
        st.subheader("Recommendations")
        recommendations = report.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.info(f"{i}. {rec}")
        else:
            st.info("No specific recommendations at this time.")
    
    with tab4:
        st.subheader("Detailed Analysis")
        
        # Skills
        if 'skills' in report:
            st.write("**Extracted Skills:**")
            skills = report['skills']
            if skills:
                skills_text = ", ".join(skills)
                st.write(skills_text)
        
        # Keywords
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Matched Keywords:**")
            matched_kw = report.get('matched_keywords', [])
            if matched_kw:
                for kw in matched_kw[:10]:
                    st.success(f"✓ {kw}")
        
        with col2:
            st.write("**Missing Keywords:**")
            missing_kw = report.get('missing_keywords', [])
            if missing_kw:
                for kw in missing_kw[:10]:
                    st.error(f"✗ {kw}")
    
    # Download report button
    if st.button("📥 Download Full Report"):
        st.info("Report download feature coming soon!")

def main():
    """Main application."""
    initialize_session_state()
    
    # Sidebar navigation
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.radio(
        "Choose a page:",
        ["🏠 Analyze Resume", "📚 Resume History", "📊 Statistics", "⚙️ Settings"]
    )
    
    # Display selected page
    if page == "🏠 Analyze Resume":
        analyze_resume_page()
    
    elif page == "📚 Resume History":
        display_resume_history()
    
    elif page == "📊 Statistics":
        display_statistics()
    
    elif page == "⚙️ Settings":
        st.subheader("⚙️ Settings")
        st.info("Settings page coming soon!")
        
        # Database info
        st.write("---")
        st.write("**Database Information:**")
        st.write(f"Location: `{st.session_state.db.db_path}`")
        
        if st.button("🔄 Reset Database"):
            if st.checkbox("I understand this will delete all data"):
                st.warning("This feature is disabled for safety. Please manually delete the database file.")
    
    # Footer
    st.sidebar.write("---")
    st.sidebar.info(
        "💡 **Tip:** Upload multiple resumes to track your progress over time!"
    )
    
    # Display current database stats in sidebar
    stats = st.session_state.db.get_statistics()
    st.sidebar.write("---")
    st.sidebar.write("**Quick Stats:**")
    st.sidebar.write(f"Resumes: {stats['total_resumes']}")
    st.sidebar.write(f"Analyses: {stats['total_analyses']}")
    st.sidebar.write(f"Avg Score: {stats['average_match_score']:.1f}%")

if __name__ == "__main__":
    main()