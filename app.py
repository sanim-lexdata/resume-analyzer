"""
Streamlit UI for AI Resume Analyzer
"""
import streamlit as st
import sys
from pathlib import Path
import json
import tempfile
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main_enhanced import EnhancedResumeAnalyzer
from src.utils.file_loader import FileLoader


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
    .score-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 10px 0;
    }
    .score-excellent {
        background-color: #d4edda;
        color: #155724;
        border: 2px solid #c3e6cb;
    }
    .score-good {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 2px solid #bee5eb;
    }
    .score-fair {
        background-color: #fff3cd;
        color: #856404;
        border: 2px solid #ffeaa7;
    }
    .score-poor {
        background-color: #f8d7da;
        color: #721c24;
        border: 2px solid #f5c6cb;
    }
    .skill-badge {
        display: inline-block;
        padding: 5px 10px;
        margin: 5px;
        border-radius: 15px;
        font-size: 0.9rem;
    }
    .skill-matched {
        background-color: #d4edda;
        color: #155724;
    }
    .skill-missing {
        background-color: #f8d7da;
        color: #721c24;
    }
    .skill-extra {
        background-color: #d1ecf1;
        color: #0c5460;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'report' not in st.session_state:
        st.session_state.report = None
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = None


def get_score_color(score):
    """Get color class based on score."""
    if score >= 80:
        return "score-excellent"
    elif score >= 70:
        return "score-good"
    elif score >= 50:
        return "score-fair"
    else:
        return "score-poor"


def display_score_box(score, rating):
    """Display main score box."""
    color_class = get_score_color(score)
    st.markdown(f"""
    <div class="score-box {color_class}">
        🎯 Overall Match Score: {score:.1f}/100<br>
        <span style="font-size: 1.2rem;">{rating}</span>
    </div>
    """, unsafe_allow_html=True)


def display_skills_section(skills_analysis):
    """Display skills analysis section."""
    st.subheader("📊 Skills Analysis")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Matched",
            skills_analysis.get('total_matched', 0),
            delta=None
        )
    
    with col2:
        st.metric(
            "Match Rate",
            f"{skills_analysis.get('match_rate', 0):.1f}%",
            delta=None
        )
    
    with col3:
        st.metric(
            "Missing Skills",
            len(skills_analysis.get('missing', [])),
            delta=None,
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            "Bonus Skills",
            len(skills_analysis.get('extra', [])),
            delta=None
        )
    
    # Matched Skills
    matched_exact = skills_analysis.get('matched_exact', [])
    matched_fuzzy = skills_analysis.get('matched_fuzzy', [])
    matched_semantic = skills_analysis.get('matched_semantic', [])
    
    if matched_exact or matched_fuzzy or matched_semantic:
        st.markdown("#### ✅ Matched Skills")
        
        tabs = st.tabs(["Exact Matches", "Similar Matches", "Semantic Matches"])
        
        with tabs[0]:
            if matched_exact:
                skills_html = "".join([
                    f'<span class="skill-badge skill-matched">{skill}</span>'
                    for skill in matched_exact[:20]
                ])
                st.markdown(skills_html, unsafe_allow_html=True)
                if len(matched_exact) > 20:
                    st.caption(f"... and {len(matched_exact) - 20} more")
            else:
                st.info("No exact matches found")
        
        with tabs[1]:
            if matched_fuzzy:
                skills_html = "".join([
                    f'<span class="skill-badge skill-matched">{skill}</span>'
                    for skill in matched_fuzzy[:20]
                ])
                st.markdown(skills_html, unsafe_allow_html=True)
                if len(matched_fuzzy) > 20:
                    st.caption(f"... and {len(matched_fuzzy) - 20} more")
            else:
                st.info("No similar matches found")
        
        with tabs[2]:
            if matched_semantic:
                skills_html = "".join([
                    f'<span class="skill-badge skill-matched">{skill}</span>'
                    for skill in matched_semantic[:20]
                ])
                st.markdown(skills_html, unsafe_allow_html=True)
                if len(matched_semantic) > 20:
                    st.caption(f"... and {len(matched_semantic) - 20} more")
            else:
                st.info("No semantic matches found")
    
    # Missing Skills
    missing_skills = skills_analysis.get('missing', [])
    if missing_skills:
        st.markdown("#### ❌ Missing Required Skills")
        skills_html = "".join([
            f'<span class="skill-badge skill-missing">{skill}</span>'
            for skill in missing_skills[:15]
        ])
        st.markdown(skills_html, unsafe_allow_html=True)
        if len(missing_skills) > 15:
            with st.expander(f"Show all {len(missing_skills)} missing skills"):
                skills_html_all = "".join([
                    f'<span class="skill-badge skill-missing">{skill}</span>'
                    for skill in missing_skills
                ])
                st.markdown(skills_html_all, unsafe_allow_html=True)
    
    # Extra Skills
    extra_skills = skills_analysis.get('extra', [])
    if extra_skills:
        with st.expander(f"➕ Bonus Skills ({len(extra_skills)})"):
            skills_html = "".join([
                f'<span class="skill-badge skill-extra">{skill}</span>'
                for skill in extra_skills[:20]
            ])
            st.markdown(skills_html, unsafe_allow_html=True)
            if len(extra_skills) > 20:
                st.caption(f"... and {len(extra_skills) - 20} more")


def display_experience_section(experience_analysis):
    """Display experience analysis section."""
    st.subheader("💼 Experience Analysis")
    
    if experience_analysis:
        message = experience_analysis.get('message', 'N/A')
        status = experience_analysis.get('status', 'unknown')
        recommendation = experience_analysis.get('recommendation', '')
        
        # Status indicator
        status_colors = {
            'meets_requirement': '🟢',
            'exceeds_requirement': '🟢',
            'close_match': '🟡',
            'moderate_gap': '🟠',
            'significant_gap': '🔴',
            'critical_gap': '🔴'
        }
        
        status_icon = status_colors.get(status, '⚪')
        
        st.markdown(f"""
        <div class="metric-card">
            <strong>{status_icon} Status:</strong> {message}<br>
            {f'<strong>💡 Recommendation:</strong> {recommendation}' if recommendation else ''}
        </div>
        """, unsafe_allow_html=True)


def display_recommendations(recommendations):
    """Display recommendations section."""
    st.subheader("💡 Recommendations")
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"**{i}.** {rec}")
    else:
        st.info("No specific recommendations at this time.")


def display_strengths(strengths):
    """Display strengths section."""
    st.subheader("🏆 Your Strengths")
    
    if strengths:
        for strength in strengths:
            st.markdown(f"✅ {strength}")
    else:
        st.info("Analysis in progress...")


def main():
    """Main Streamlit app."""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">📄 AI Resume Analyzer</div>', unsafe_allow_html=True)
    st.markdown("### Powered by Machine Learning & NLP")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/resume.png", width=100)
        st.title("Upload Documents")
        
        # Resume upload
        st.subheader("1️⃣ Upload Resume")
        resume_file = st.file_uploader(
            "Choose your resume",
            type=['pdf', 'docx', 'txt'],
            help="Supported formats: PDF, DOCX, TXT"
        )
        
        # Job description input
        st.subheader("2️⃣ Job Description")
        jd_input_method = st.radio(
            "Input method:",
            ["Paste Text", "Upload File"]
        )
        
        if jd_input_method == "Paste Text":
            jd_text = st.text_area(
                "Paste job description here",
                height=200,
                placeholder="Paste the complete job description..."
            )
        else:
            jd_file = st.file_uploader(
                "Upload JD file",
                type=['txt'],
                help="Plain text file only"
            )
            jd_text = ""
            if jd_file:
                jd_text = jd_file.read().decode('utf-8')
        
        # Job title
        st.subheader("3️⃣ Job Title (Optional)")
        job_title = st.text_input(
            "Job title",
            placeholder="e.g., Senior Software Engineer"
        )
        
        # Analyze button
        st.markdown("---")
        analyze_button = st.button(
            "🚀 Analyze Resume",
            type="primary",
            use_container_width=True
        )
        
        # Settings
        with st.expander("⚙️ Advanced Settings"):
            fuzzy_threshold = st.slider(
                "Fuzzy Match Threshold",
                50, 100, 85,
                help="Minimum similarity for fuzzy skill matching"
            )
            semantic_threshold = st.slider(
                "Semantic Match Threshold",
                50, 100, 70,
                help="Minimum similarity for semantic skill matching"
            )
    
    # Main content area
    if analyze_button:
        if not resume_file:
            st.error("❌ Please upload a resume file!")
            return
        
        if not jd_text or len(jd_text.strip()) < 50:
            st.error("❌ Please provide a job description (at least 50 characters)!")
            return
        
        # Process analysis
        with st.spinner("🔄 Analyzing resume... This may take 30-60 seconds..."):
            try:
                # Save uploaded resume to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(resume_file.name).suffix) as tmp_file:
                    tmp_file.write(resume_file.getvalue())
                    tmp_resume_path = tmp_file.name
                
                # Initialize analyzer
                if st.session_state.analyzer is None:
                    st.session_state.analyzer = EnhancedResumeAnalyzer()
                
                # Run analysis
                report = st.session_state.analyzer.analyze(
                    tmp_resume_path,
                    jd_text,
                    job_title or "Position"
                )
                
                # Clean up temp file
                os.unlink(tmp_resume_path)
                
                # Store results
                st.session_state.report = report
                st.session_state.analysis_complete = True
                
                st.success("✅ Analysis complete!")
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                import traceback
                with st.expander("Show error details"):
                    st.code(traceback.format_exc())
                return
    
    # Display results
    if st.session_state.analysis_complete and st.session_state.report:
        report = st.session_state.report
        
        # Overall score
        overall = report.get('overall_score', {})
        final_score = overall.get('final_score', 0)
        rating = overall.get('rating', 'N/A')
        
        display_score_box(final_score, rating)
        
        # Score breakdown
        st.markdown("---")
        st.subheader("📈 Score Breakdown")
        
        breakdown = overall.get('breakdown', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            skill_score = breakdown.get('skill_score', 0)
            st.metric("Skills", f"{skill_score:.1f}/100")
            st.progress(skill_score / 100)
        
        with col2:
            semantic_score = breakdown.get('semantic_score', 0)
            st.metric("Semantic", f"{semantic_score:.1f}/100")
            st.progress(semantic_score / 100)
        
        with col3:
            experience_score = breakdown.get('experience_score', 0)
            st.metric("Experience", f"{experience_score:.1f}/100")
            st.progress(experience_score / 100)
        
        with col4:
            qual_score = breakdown.get('qualification_score', 0)
            st.metric("Qualifications", f"{qual_score:.1f}/100")
            st.progress(qual_score / 100)
        
        st.markdown("---")
        
        # Tabs for detailed analysis
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Skills Analysis",
            "💼 Experience",
            "💡 Recommendations",
            "📄 Full Report"
        ])
        
        with tab1:
            skills_analysis = report.get('skills_analysis', {})
            display_skills_section(skills_analysis)
        
        with tab2:
            experience_analysis = report.get('experience_analysis', {})
            display_experience_section(experience_analysis)
            
            # Strengths
            strengths = report.get('strengths', [])
            if strengths:
                st.markdown("---")
                display_strengths(strengths)
        
        with tab3:
            recommendations = report.get('recommendations', [])
            display_recommendations(recommendations)
        
        with tab4:
            st.subheader("📄 Complete Analysis Report")
            
            # Summary
            summary = report.get('summary', '')
            if summary:
                st.info(summary)
            
            # Download options
            col1, col2 = st.columns(2)
            
            with col1:
                # Download JSON
                json_str = json.dumps(report, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Download JSON Report",
                    data=json_str,
                    file_name=f"resume_analysis_{final_score:.0f}.json",
                    mime="application/json"
                )
            
            with col2:
                # Download text report
                text_report = generate_text_report(report)
                st.download_button(
                    label="📥 Download Text Report",
                    data=text_report,
                    file_name=f"resume_analysis_{final_score:.0f}.txt",
                    mime="text/plain"
                )
            
            # Display full JSON
            with st.expander("🔍 View Full JSON Report"):
                st.json(report)
    
    else:
        # Welcome message
        st.info("""
        ### 👋 Welcome to AI Resume Analyzer!
        
        **How to use:**
        1. Upload your resume (PDF, DOCX, or TXT)
        2. Paste or upload the job description
        3. Optionally enter the job title
        4. Click "Analyze Resume" button
        
        **What you'll get:**
        - Overall match score (0-100)
        - Detailed skill analysis (matched, missing, bonus)
        - Experience gap analysis
        - Personalized recommendations
        - Downloadable reports
        
        **Features:**
        ✨ AI-powered skill extraction
        🎯 Semantic similarity analysis
        📊 Comprehensive scoring
        💡 Actionable recommendations
        """)


def generate_text_report(report):
    """Generate text version of report."""
    lines = []
    lines.append("=" * 80)
    lines.append("AI RESUME ANALYSIS REPORT")
    lines.append("=" * 80)
    lines.append("")
    
    # Overall score
    overall = report.get('overall_score', {})
    lines.append(f"OVERALL SCORE: {overall.get('final_score', 0):.1f}/100")
    lines.append(f"Rating: {overall.get('rating', 'N/A')}")
    lines.append("")
    
    # Breakdown
    breakdown = overall.get('breakdown', {})
    lines.append("SCORE BREAKDOWN:")
    lines.append(f"  • Skills: {breakdown.get('skill_score', 0):.1f}/100")
    lines.append(f"  • Semantic Similarity: {breakdown.get('semantic_score', 0):.1f}/100")
    lines.append(f"  • Experience: {breakdown.get('experience_score', 0):.1f}/100")
    lines.append(f"  • Qualifications: {breakdown.get('qualification_score', 0):.1f}/100")
    lines.append("")
    
    # Skills
    skills = report.get('skills_analysis', {})
    lines.append("SKILLS ANALYSIS:")
    lines.append(f"  Total Matched: {skills.get('total_matched', 0)}")
    lines.append(f"  Match Rate: {skills.get('match_rate', 0):.1f}%")
    lines.append(f"  Missing: {len(skills.get('missing', []))}")
    lines.append("")
    
    # Recommendations
    recommendations = report.get('recommendations', [])
    if recommendations:
        lines.append("RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"  {i}. {rec}")
        lines.append("")
    
    lines.append("=" * 80)
    
    return "\n".join(lines)


if __name__ == "__main__":
    main()