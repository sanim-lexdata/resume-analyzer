import streamlit as st
import os
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd
import PyPDF2
import docx

# Import only database
from src.database import ResumeDatabase

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

# Simple Resume Analyzer Class
class SimpleResumeAnalyzer:
    """Simple resume analyzer without external dependencies."""
    
    def __init__(self):
        self.common_skills = [
            'Python', 'Java', 'JavaScript', 'SQL', 'HTML', 'CSS', 
            'React', 'Node.js', 'Git', 'Docker', 'AWS', 'Azure',
            'Machine Learning', 'Data Analysis', 'Project Management',
            'Communication', 'Leadership', 'Problem Solving'
        ]
    
    def extract_text(self, file_path):
        """Extract text from PDF, DOCX, or TXT files."""
        try:
            if file_path.endswith('.pdf'):
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            
            elif file_path.endswith('.docx'):
                doc = docx.Document(file_path)
                text = '\n'.join([para.text for para in doc.paragraphs])
                return text
            
            else:  # .txt
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    return file.read()
        
        except Exception as e:
            st.error(f"Error extracting text: {str(e)}")
            return ""
    
    def extract_skills(self, text):
        """Extract skills from resume text."""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def calculate_ats_score(self, text):
        """Calculate ATS compatibility score."""
        score = 70  # Base score
        
        # Check for good formatting
        if len(text) > 500:
            score += 5
        if '@' in text:  # Has email
            score += 5
        if any(word in text.lower() for word in ['experience', 'education', 'skills']):
            score += 10
        if text.count('\n') > 10:  # Well-structured
            score += 10
        
        return min(score, 100)
    
    def calculate_match_score(self, resume_text, job_description):
        """Calculate match score between resume and job description."""
        if not job_description:
            return 75.0
        
        resume_words = set(resume_text.lower().split())
        job_words = set(job_description.lower().split())
        
        # Find common words (excluding common words)
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        resume_words -= common_words
        job_words -= common_words
        
        if not job_words:
            return 75.0
        
        matches = resume_words.intersection(job_words)
        score = (len(matches) / len(job_words)) * 100
        
        return min(score, 100)
    
    def analyze(self, resume_path, job_description=None):
        """Perform complete resume analysis."""
        text = self.extract_text(resume_path)
        
        if not text:
            return None
        
        # Extract information
        skills = self.extract_skills(text)
        ats_score = self.calculate_ats_score(text)
        match_score = self.calculate_match_score(text, job_description or "")
        
        # Generate analysis
        strengths = []
        weaknesses = []
        recommendations = []
        
        if len(skills) >= 5:
            strengths.append(f"Strong skill set with {len(skills)} identified skills")
        else:
            weaknesses.append("Limited technical skills mentioned")
            recommendations.append("Add more technical skills to your resume")
        
        if len(text) > 1000:
            strengths.append("Comprehensive resume with detailed information")
        else:
            weaknesses.append("Resume might be too brief")
            recommendations.append("Add more details about your experience and achievements")
        
        if '@' in text:
            strengths.append("Contact information included")
        else:
            weaknesses.append("Missing contact information")
            recommendations.append("Add email address to your resume")
        
        # Keywords
        job_keywords = []
        if job_description:
            job_keywords = [word for word in self.common_skills 
                          if word.lower() in job_description.lower()]
        
        matched_keywords = [skill for skill in skills if skill in job_keywords] if job_keywords else skills
        missing_keywords = [kw for kw in job_keywords if kw not in matched_keywords]
        
        return {
            'match_score': match_score,
            'ats_score': ats_score,
            'matched_keywords': matched_keywords,
            'missing_keywords': missing_keywords,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'recommendations': recommendations,
            'skills': skills,
            'contact_info': {
                'email': self.extract_email(text),
                'phone': self.extract_phone(text)
            }
        }
    
    def extract_email(self, text):
        """Extract email from text."""
        import re
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        return emails[0] if emails else None
    
    def extract_phone(self, text):
        """Extract phone number from text."""
        import re
        phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
        return phones[0] if phones else None

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables."""
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = SimpleResumeAnalyzer()
    
    if 'db' not in st.session_state:
        st.session_state.db = ResumeDatabase()
    
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    
    if 'current_resume_id' not in st.session_state:
        st.session_state.current_resume_id = None

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
                analyses = st.session_state.db.get_analysis_results(resume['id'])
                st.write(f"**Total Analyses:** {len(analyses)}")
                
                if analyses:
                    latest = analyses[0]
                    st.write(f"**Latest Match Score:** {latest['match_score']:.1f}%")
                    st.write(f"**Latest ATS Score:** {latest['ats_score']:.1f}%")
            
            if analyses:
                st.write("---")
                st.write("**Analysis History:**")
                for i, analysis in enumerate(analyses, 1):
                    st.write(f"{i}. {analysis['analysis_date'][:16]} - Match: {analysis['match_score']:.1f}% | ATS: {analysis['ats_score']:.1f}%")
            
            if st.button(f"🗑️ Delete Resume", key=f"delete_{resume['id']}"):
                st.session_state.db.delete_resume(resume['id'])
                st.success("Resume deleted!")
                st.rerun()

def display_statistics():
    """Display database statistics."""
    st.subheader("📊 Statistics Dashboard")
    
    stats = st.session_state.db.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Resumes", stats['total_resumes'])
    
    with col2:
        st.metric("Job Descriptions", stats['total_jobs'])
    
    with col3:
        st.metric("Total Analyses", stats['total_analyses'])
    
    with col4:
        st.metric("Avg Match Score", f"{stats['average_match_score']:.1f}%")
    
    resumes = st.session_state.db.get_all_resumes()
    
    if resumes:
        st.write("---")
        viz_data = []
        for resume in resumes:
            analyses = st.session_state.db.get_analysis_results(resume['id'])
            for analysis in analyses:
                viz_data.append({
                    'Resume': resume['filename'][:20],
                    'Date': analysis['analysis_date'][:10],
                    'Match Score': analysis['match_score'],
                    'ATS Score': analysis['ats_score']
                })
        
        if viz_data:
            df = pd.DataFrame(viz_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = px.histogram(df, x='Match Score', nbins=10, title='Match Score Distribution')
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = px.histogram(df, x='ATS Score', nbins=10, title='ATS Score Distribution')
                st.plotly_chart(fig2, use_container_width=True)

def analyze_resume_page():
    """Main resume analysis page."""
    st.markdown('<div class="main-header">🤖 AI Resume Analyzer</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF, DOCX, or TXT)",
        type=['pdf', 'docx', 'txt'],
        help="Upload your resume for analysis"
    )
    
    with st.expander("📋 Add Job Description (Optional)", expanded=False):
        job_title = st.text_input("Job Title")
        company_name = st.text_input("Company Name")
        job_description = st.text_area("Job Description", height=200)
    
    if uploaded_file and st.button("🚀 Analyze Resume", type="primary"):
        with st.spinner("Analyzing your resume..."):
            try:
                file_path = save_uploaded_file(uploaded_file)
                resume_text = st.session_state.analyzer.extract_text(file_path)
                
                resume_id = st.session_state.db.insert_resume(
                    filename=uploaded_file.name,
                    file_size=uploaded_file.size,
                    file_type=uploaded_file.type.split('/')[-1] if '/' in uploaded_file.type else uploaded_file.type,
                    full_text=resume_text
                )
                
                job_id = None
                if job_description:
                    job_id = st.session_state.db.insert_job_description(
                        title=job_title or "N/A",
                        company=company_name or "N/A",
                        description=job_description,
                        requirements=""
                    )
                
                report = st.session_state.analyzer.analyze(file_path, job_description)
                
                if report:
                    analysis_id = st.session_state.db.insert_analysis_result(
                        resume_id=resume_id,
                        job_id=job_id,
                        match_score=report['match_score'],
                        ats_score=report['ats_score'],
                        keyword_match_count=len(report['matched_keywords']),
                        missing_keywords=report['missing_keywords'],
                        strengths=report['strengths'],
                        weaknesses=report['weaknesses'],
                        recommendations=report['recommendations'],
                        detailed_analysis=report
                    )
                    
                    if report['skills']:
                        skills_list = [{'name': skill, 'category': 'General', 'confidence': 1.0} 
                                      for skill in report['skills']]
                        st.session_state.db.insert_skills(resume_id, skills_list)
                    
                    if report['contact_info']:
                        st.session_state.db.insert_contact_info(
                            resume_id=resume_id,
                            email=report['contact_info'].get('email'),
                            phone=report['contact_info'].get('phone')
                        )
                    
                    st.session_state.analysis_report = report
                    st.session_state.analysis_complete = True
                    st.success("✅ Analysis completed and saved to database!")
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
    
    if st.session_state.analysis_complete and 'analysis_report' in st.session_state:
        display_analysis_results(st.session_state.analysis_report)

def display_analysis_results(report):
    """Display analysis results."""
    st.write("---")
    st.header("📊 Analysis Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Match Score", f"{report['match_score']:.1f}%")
    
    with col2:
        st.metric("ATS Compatibility", f"{report['ats_score']:.1f}%")
    
    with col3:
        matched = len(report['matched_keywords'])
        total = matched + len(report['missing_keywords'])
        st.metric("Keywords Matched", f"{matched}/{total if total > 0 else matched}")
    
    tab1, tab2, tab3, tab4 = st.tabs(["💪 Strengths", "⚠️ Weaknesses", "💡 Recommendations", "🔍 Details"])
    
    with tab1:
        st.subheader("Strengths")
        for strength in report['strengths']:
            st.success(f"✓ {strength}")
    
    with tab2:
        st.subheader("Areas for Improvement")
        for weakness in report['weaknesses']:
            st.warning(f"• {weakness}")
    
    with tab3:
        st.subheader("Recommendations")
        for i, rec in enumerate(report['recommendations'], 1):
            st.info(f"{i}. {rec}")
    
    with tab4:
        st.subheader("Detailed Analysis")
        
        if report['skills']:
            st.write("**Extracted Skills:**")
            st.write(", ".join(report['skills']))
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Matched Keywords:**")
            for kw in report['matched_keywords'][:10]:
                st.success(f"✓ {kw}")
        
        with col2:
            st.write("**Missing Keywords:**")
            for kw in report['missing_keywords'][:10]:
                st.error(f"✗ {kw}")

def main():
    """Main application."""
    initialize_session_state()
    
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.radio(
        "Choose a page:",
        ["🏠 Analyze Resume", "📚 Resume History", "📊 Statistics"]
    )
    
    if page == "🏠 Analyze Resume":
        analyze_resume_page()
    elif page == "📚 Resume History":
        display_resume_history()
    elif page == "📊 Statistics":
        display_statistics()
    
    st.sidebar.write("---")
    stats = st.session_state.db.get_statistics()
    st.sidebar.write("**Quick Stats:**")
    st.sidebar.write(f"Resumes: {stats['total_resumes']}")
    st.sidebar.write(f"Analyses: {stats['total_analyses']}")
    st.sidebar.write(f"Avg Score: {stats['average_match_score']:.1f}%")

if __name__ == "__main__":
    main()