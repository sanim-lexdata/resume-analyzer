import streamlit as st
import os
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import PyPDF2
import docx
import re
from datetime import datetime
from collections import Counter

from src.database import ResumeDatabase

# Page configuration
st.set_page_config(
    page_title="Multi-Resume Analyzer & Comparator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1f77b4, #2ca02c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .rank-card {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .rank-1 { background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); }
    .rank-2 { background: linear-gradient(135deg, #C0C0C0 0%, #A9A9A9 100%); }
    .rank-3 { background: linear-gradient(135deg, #CD7F32 0%, #8B4513 100%); }
    .rank-other { background: linear-gradient(135deg, #E8E8E8 0%, #D3D3D3 100%); }
    
    .metric-box {
        background: white;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

class AdvancedResumeAnalyzer:
    """Advanced resume analyzer with dynamic skill extraction."""
    
    def __init__(self):
        self.technical_keywords = set([
            'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift',
            'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'express',
            'sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'ci/cd',
            'machine learning', 'deep learning', 'ai', 'data science', 'nlp', 'computer vision',
            'agile', 'scrum', 'devops', 'microservices', 'rest', 'graphql', 'api'
        ])
    
    def extract_text(self, file_path):
        """Extract text from PDF, DOCX, or TXT files."""
        try:
            if file_path.endswith('.pdf'):
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text.strip()
            
            elif file_path.endswith('.docx'):
                doc = docx.Document(file_path)
                text = '\n'.join([para.text for para in doc.paragraphs])
                return text.strip()
            
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    return file.read().strip()
        
        except Exception as e:
            return f"Error extracting text: {str(e)}"
    
    def extract_dynamic_skills(self, text):
        """Extract skills dynamically from text without predefined list."""
        text_lower = text.lower()
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#./-]*\b', text_lower)
        
        # Extract multi-word technical terms
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)]
        
        all_terms = set(words + bigrams + trigrams)
        
        # Find technical skills
        found_skills = set()
        for term in all_terms:
            if term in self.technical_keywords:
                found_skills.add(term)
        
        # Look for years of experience
        experience_matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)', text_lower)
        years_exp = max([int(y) for y in experience_matches], default=0)
        
        return list(found_skills), years_exp
    
    def extract_sections(self, text):
        """Extract different sections from resume."""
        sections = {
            'education': '',
            'experience': '',
            'skills': '',
            'projects': '',
            'certifications': ''
        }
        
        text_lower = text.lower()
        
        # Find section headers
        section_patterns = {
            'education': r'education|academic|qualification|degree',
            'experience': r'experience|employment|work history|professional',
            'skills': r'skills|technical|competencies|expertise',
            'projects': r'projects|portfolio',
            'certifications': r'certifications?|licenses?|awards?'
        }
        
        for section, pattern in section_patterns.items():
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                start = match.start()
                # Get text after section header (next 500 chars)
                sections[section] += text[start:start+500] + " "
        
        return sections
    
    def calculate_keyword_match(self, resume_text, job_description):
        """Calculate keyword match percentage dynamically."""
        if not job_description:
            return 50.0, [], []
        
        # Extract words from both texts
        resume_words = set(re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#./-]*\b', resume_text.lower()))
        job_words = set(re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#./-]*\b', job_description.lower()))
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
                     'can', 'could', 'may', 'might', 'must', 'shall', 'this', 'that', 'these', 'those'}
        
        resume_words -= stop_words
        job_words -= stop_words
        
        # Filter for meaningful words (3+ characters)
        job_words = {w for w in job_words if len(w) >= 3}
        resume_words = {w for w in resume_words if len(w) >= 3}
        
        # Calculate matches
        matched = resume_words.intersection(job_words)
        missing = job_words - resume_words
        
        if len(job_words) == 0:
            return 50.0, list(matched)[:20], list(missing)[:20]
        
        match_score = (len(matched) / len(job_words)) * 100
        
        return match_score, list(matched)[:20], list(missing)[:20]
    
    def calculate_ats_score(self, text, sections):
        """Calculate ATS compatibility score."""
        score = 0
        
        # Length check (30 points)
        word_count = len(text.split())
        if 300 <= word_count <= 800:
            score += 30
        elif 200 <= word_count < 300 or 800 < word_count <= 1200:
            score += 20
        else:
            score += 10
        
        # Section structure (25 points)
        has_sections = sum([1 for s in sections.values() if s.strip()])
        score += min(has_sections * 5, 25)
        
        # Contact information (15 points)
        has_email = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text))
        has_phone = bool(re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text))
        if has_email:
            score += 8
        if has_phone:
            score += 7
        
        # Formatting (15 points)
        has_bullets = '•' in text or '-' in text
        has_numbers = bool(re.search(r'\d+', text))
        if has_bullets:
            score += 8
        if has_numbers:
            score += 7
        
        # Keywords density (15 points)
        technical_count = sum([1 for kw in self.technical_keywords if kw in text.lower()])
        score += min(technical_count * 2, 15)
        
        return min(score, 100)
    
    def analyze_resume(self, file_path, job_description=None, filename=None):
        """Comprehensive resume analysis."""
        text = self.extract_text(file_path)
        
        if not text or text.startswith("Error"):
            return None
        
        # Extract information
        sections = self.extract_sections(text)
        skills, years_exp = self.extract_dynamic_skills(text)
        match_score, matched_keywords, missing_keywords = self.calculate_keyword_match(text, job_description)
        ats_score = self.calculate_ats_score(text, sections)
        
        # Calculate overall score (weighted average)
        overall_score = (match_score * 0.5) + (ats_score * 0.3) + (min(len(skills) * 2, 20) * 0.2)
        
        # Generate strengths and weaknesses
        strengths = []
        weaknesses = []
        recommendations = []
        
        if len(skills) >= 8:
            strengths.append(f"Strong technical profile with {len(skills)} identified skills")
        elif len(skills) < 5:
            weaknesses.append("Limited technical skills mentioned")
            recommendations.append("Add more relevant technical skills")
        
        if years_exp >= 5:
            strengths.append(f"Significant experience: {years_exp}+ years")
        elif years_exp > 0:
            strengths.append(f"Relevant experience: {years_exp} years")
        
        if ats_score >= 80:
            strengths.append("Excellent ATS compatibility")
        elif ats_score < 60:
            weaknesses.append("Low ATS compatibility score")
            recommendations.append("Improve resume formatting for ATS systems")
        
        if match_score >= 70:
            strengths.append(f"High keyword match: {match_score:.0f}%")
        elif match_score < 40:
            weaknesses.append("Low keyword match with job description")
            recommendations.append("Tailor resume to include more relevant keywords")
        
        if len(matched_keywords) < 5:
            recommendations.append("Include more keywords from the job description")
        
        if not sections['education'].strip():
            weaknesses.append("Education section not clearly identified")
            recommendations.append("Add a clear Education section")
        
        return {
            'filename': filename or os.path.basename(file_path),
            'overall_score': round(overall_score, 2),
            'match_score': round(match_score, 2),
            'ats_score': round(ats_score, 2),
            'skills': skills,
            'years_experience': years_exp,
            'matched_keywords': matched_keywords,
            'missing_keywords': missing_keywords,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'recommendations': recommendations,
            'word_count': len(text.split()),
            'sections': sections,
            'full_text': text
        }

def initialize_session_state():
    """Initialize session state."""
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = AdvancedResumeAnalyzer()
    
    if 'db' not in st.session_state:
        st.session_state.db = ResumeDatabase()
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = []
    
    if 'job_description' not in st.session_state:
        st.session_state.job_description = ""

def save_uploaded_file(uploaded_file):
    """Save uploaded file."""
    upload_dir = Path("output/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = upload_dir / f"{timestamp}_{uploaded_file.name}"
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return str(file_path)

def display_comparison_dashboard():
    """Display comparison dashboard for multiple resumes."""
    results = st.session_state.analysis_results
    
    if not results:
        st.info("Upload resumes and job description to see comparison")
        return
    
    st.markdown('<div class="main-header">📊 Resume Comparison Dashboard</div>', unsafe_allow_html=True)
    
    # Sort by overall score
    sorted_results = sorted(results, key=lambda x: x['overall_score'], reverse=True)
    
    # Summary metrics
    st.subheader("📈 Overall Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Resumes", len(results))
    
    with col2:
        avg_score = sum([r['overall_score'] for r in results]) / len(results)
        st.metric("Average Score", f"{avg_score:.1f}%")
    
    with col3:
        best_score = sorted_results[0]['overall_score']
        st.metric("Best Score", f"{best_score:.1f}%")
    
    with col4:
        avg_match = sum([r['match_score'] for r in results]) / len(results)
        st.metric("Avg Match", f"{avg_match:.1f}%")
    
    # Rankings
    st.subheader("🏆 Resume Rankings")
    
    for idx, result in enumerate(sorted_results, 1):
        rank_class = f"rank-{idx}" if idx <= 3 else "rank-other"
        
        with st.container():
            st.markdown(f'<div class="rank-card {rank_class}">', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
            
            with col1:
                medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"#{idx}"
                st.markdown(f"### {medal}")
            
            with col2:
                st.markdown(f"**{result['filename']}**")
                st.caption(f"Overall Score: {result['overall_score']:.1f}%")
            
            with col3:
                st.metric("Match", f"{result['match_score']:.1f}%")
                st.metric("ATS", f"{result['ats_score']:.1f}%")
            
            with col4:
                st.metric("Skills", len(result['skills']))
                st.metric("Experience", f"{result['years_experience']}y")
            
            # Expandable details
            with st.expander("📋 View Details"):
                tab1, tab2, tab3 = st.tabs(["Strengths", "Weaknesses", "Keywords"])
                
                with tab1:
                    for strength in result['strengths']:
                        st.success(f"✓ {strength}")
                
                with tab2:
                    for weakness in result['weaknesses']:
                        st.warning(f"⚠ {weakness}")
                    st.write("**Recommendations:**")
                    for rec in result['recommendations']:
                        st.info(f"💡 {rec}")
                
                with tab3:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Matched Keywords:**")
                        for kw in result['matched_keywords'][:10]:
                            st.success(f"✓ {kw}")
                    with col2:
                        st.write("**Missing Keywords:**")
                        for kw in result['missing_keywords'][:10]:
                            st.error(f"✗ {kw}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Visualizations
    st.subheader("📊 Visual Comparison")
    
    # Create DataFrame
    df = pd.DataFrame([{
        'Resume': r['filename'][:20],
        'Overall': r['overall_score'],
        'Match': r['match_score'],
        'ATS': r['ats_score'],
        'Skills': len(r['skills'])
    } for r in sorted_results])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart - Overall scores
        fig1 = px.bar(df, x='Resume', y='Overall', 
                     title='Overall Scores Comparison',
                     color='Overall',
                     color_continuous_scale='Blues')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Radar chart - Top 3 resumes
        if len(df) >= 3:
            top3 = df.head(3)
            fig2 = go.Figure()
            
            for idx, row in top3.iterrows():
                fig2.add_trace(go.Scatterpolar(
                    r=[row['Overall'], row['Match'], row['ATS'], row['Skills']*5],
                    theta=['Overall', 'Match', 'ATS', 'Skills'],
                    fill='toself',
                    name=row['Resume']
                ))
            
            fig2.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                title="Top 3 Resumes - Multi-Metric Comparison"
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    # Score distribution
    fig3 = px.box(df, y=['Overall', 'Match', 'ATS'], 
                  title='Score Distribution Across All Resumes')
    st.plotly_chart(fig3, use_container_width=True)

def main():
    """Main application."""
    initialize_session_state()
    
    st.sidebar.title("⚙️ Configuration")
    
    # Job Description Input
    with st.sidebar.expander("📋 Job Description", expanded=True):
        job_title = st.text_input("Job Title")
        company = st.text_input("Company")
        job_desc = st.text_area("Job Description", height=200, 
                                placeholder="Paste the complete job description here...")
        
        if st.button("💾 Save Job Description"):
            st.session_state.job_description = job_desc
            if job_desc:
                st.success("Job description saved!")
    
    # Main content
    st.markdown('<div class="main-header">🎯 Multi-Resume Analyzer & Comparator</div>', unsafe_allow_html=True)
    
    st.info("📤 Upload multiple resumes to compare them against the job description")
    
    # File uploader - Multiple files
    uploaded_files = st.file_uploader(
        "Upload Resumes (PDF, DOCX, TXT)",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help="You can select multiple files at once"
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} resume(s) uploaded")
    
    with col2:
        analyze_button = st.button("🚀 Analyze All Resumes", type="primary", disabled=not uploaded_files)
    
    # Analysis
    if analyze_button and uploaded_files:
        st.session_state.analysis_results = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Analyzing: {uploaded_file.name}...")
            
            try:
                # Save file
                file_path = save_uploaded_file(uploaded_file)
                
                # Analyze
                result = st.session_state.analyzer.analyze_resume(
                    file_path,
                    st.session_state.job_description,
                    uploaded_file.name
                )
                
                if result:
                    st.session_state.analysis_results.append(result)
                    
                    # Save to database
                    resume_id = st.session_state.db.insert_resume(
                        filename=uploaded_file.name,
                        file_size=uploaded_file.size,
                        file_type=uploaded_file.type.split('/')[-1] if '/' in uploaded_file.type else 'unknown',
                        full_text=result['full_text']
                    )
                    
                    # Save analysis
                    job_id = None
                    if st.session_state.job_description and job_title:
                        job_id = st.session_state.db.insert_job_description(
                            title=job_title,
                            company=company or "N/A",
                            description=st.session_state.job_description,
                            requirements=""
                        )
                    
                    st.session_state.db.insert_analysis_result(
                        resume_id=resume_id,
                        job_id=job_id,
                        match_score=result['match_score'],
                        ats_score=result['ats_score'],
                        keyword_match_count=len(result['matched_keywords']),
                        missing_keywords=result['missing_keywords'],
                        strengths=result['strengths'],
                        weaknesses=result['weaknesses'],
                        recommendations=result['recommendations'],
                        detailed_analysis=result
                    )
                    
                    # Save skills
                    if result['skills']:
                        skills_list = [{'name': skill, 'category': 'Technical', 'confidence': 1.0} 
                                      for skill in result['skills']]
                        st.session_state.db.insert_skills(resume_id, skills_list)
                
            except Exception as e:
                st.error(f"Error analyzing {uploaded_file.name}: {str(e)}")
            
            progress_bar.progress((idx + 1) / len(uploaded_files))
        
        status_text.text("✅ Analysis complete!")
        st.success(f"Successfully analyzed {len(st.session_state.analysis_results)} resume(s)")
    
    # Display results
    if st.session_state.analysis_results:
        display_comparison_dashboard()
    
    # Sidebar stats
    st.sidebar.write("---")
    st.sidebar.subheader("📊 Database Stats")
    stats = st.session_state.db.get_statistics()
    st.sidebar.write(f"Total Resumes: {stats['total_resumes']}")
    st.sidebar.write(f"Total Analyses: {stats['total_analyses']}")
    st.sidebar.write(f"Avg Score: {stats['average_match_score']:.1f}%")

if __name__ == "__main__":
    main()