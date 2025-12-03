import streamlit as st
import io
import re
from datetime import datetime
from pathlib import Path
import json

# PDF and DOCX handling
try:
    from PyPDF2 import PdfReader
except:
    PdfReader = None

try:
    from docx import Document
except:
    Document = None

# Database
try:
    from src.database import ResumeDatabase
except:
    ResumeDatabase = None

# Page config
st.set_page_config(
    page_title="Resume Matcher - Detailed Comparison",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .skill-match {
        background: #d4edda;
        padding: 5px 10px;
        border-radius: 5px;
        margin: 2px;
        display: inline-block;
    }
    .skill-missing {
        background: #f8d7da;
        padding: 5px 10px;
        border-radius: 5px;
        margin: 2px;
        display: inline-block;
    }
    .skill-partial {
        background: #fff3cd;
        padding: 5px 10px;
        border-radius: 5px;
        margin: 2px;
        display: inline-block;
    }
    .skill-extra {
        background: #cfe2ff;
        padding: 5px 10px;
        border-radius: 5px;
        margin: 2px;
        display: inline-block;
    }
    .score-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .candidate-name {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 5px;
    }
    .filename-subtitle {
        font-size: 0.9rem;
        color: #7f8c8d;
    }
</style>
""", unsafe_allow_html=True)

class TextExtractor:
    """Extract text from various file formats"""
    
    @staticmethod
    def extract_from_pdf(file):
        if PdfReader is None:
            return "PDF support not available. Install PyPDF2."
        try:
            pdf = PdfReader(file)
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    
    @staticmethod
    def extract_from_docx(file):
        if Document is None:
            return "DOCX support not available. Install python-docx."
        try:
            doc = Document(file)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text.strip()
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"
    
    @staticmethod
    def extract_from_txt(file):
        try:
            return file.read().decode('utf-8')
        except:
            return file.read().decode('latin-1')
    
    @classmethod
    def extract(cls, file):
        filename = file.name.lower()
        if filename.endswith('.pdf'):
            return cls.extract_from_pdf(file)
        elif filename.endswith('.docx'):
            return cls.extract_from_docx(file)
        else:
            return cls.extract_from_txt(file)

class ResumeAnalyzer:
    """Analyze and compare resumes with job descriptions"""
    
    def __init__(self):
        self.jd_skills = []
        self.jd_keywords = []
        self.jd_requirements = []
    
    def extract_person_name(self, text):
        """Extract person's name from resume (usually at the top)."""
        lines = text.strip().split('\n')
        
        # Check first 5 lines for name
        for line in lines[:5]:
            line = line.strip()
            # Name is usually 2-4 words, all capitalized, no numbers
            words = line.split()
            if 2 <= len(words) <= 4:
                # Check if all words start with capital and no numbers
                if all(w[0].isupper() and not any(c.isdigit() for c in w) for w in words if len(w) > 1):
                    # Avoid common headers
                    if not any(header in line.lower() for header in ['resume', 'curriculum', 'cv', 'contact', 'email', 'phone', 'address']):
                        return line
        
        # Fallback: look for name pattern anywhere in first 500 chars
        first_section = text[:500]
        name_pattern = r'\b([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\b'
        matches = re.findall(name_pattern, first_section)
        if matches:
            return matches[0]
        
        return "Unknown Candidate"
    
    def extract_skills(self, text):
        """Extract skills from text"""
        text_lower = text.lower()
        
        # Common skill patterns
        skills = set()
        
        # Programming languages
        prog_langs = ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 
                      'kotlin', 'go', 'rust', 'typescript', 'r', 'matlab', 'scala']
        
        # Frameworks and libraries
        frameworks = ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'node.js', 
                     'express', 'fastapi', 'laravel', 'rails', '.net', 'tensorflow', 
                     'pytorch', 'keras', 'pandas', 'numpy']
        
        # Tools and technologies
        tools = ['git', 'docker', 'kubernetes', 'jenkins', 'aws', 'azure', 'gcp', 'sql', 
                'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch', 
                'tableau', 'power bi', 'excel', 'jira', 'confluence']
        
        # Soft skills
        soft_skills = ['leadership', 'communication', 'teamwork', 'problem solving', 
                      'critical thinking', 'project management', 'agile', 'scrum', 
                      'collaboration', 'analytical', 'creativity']
        
        # Check for all skill types
        all_skills = prog_langs + frameworks + tools + soft_skills
        
        for skill in all_skills:
            if skill.lower() in text_lower:
                skills.add(skill.title())
        
        # Extract years of experience
        exp_pattern = r'(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)'
        exp_matches = re.findall(exp_pattern, text_lower)
        if exp_matches:
            skills.add(f"{exp_matches[0]}+ Years Experience")
        
        # Extract education keywords
        education_keywords = ['bachelor', 'master', 'phd', 'mba', 'degree', 'university', 
                             'college', 'engineering', 'computer science', 'bsc', 'msc']
        for edu in education_keywords:
            if edu in text_lower:
                skills.add(edu.title())
        
        # Extract certification keywords
        cert_keywords = ['certified', 'certification', 'aws certified', 'pmp', 'cissp', 
                        'comptia', 'microsoft certified', 'google certified']
        for cert in cert_keywords:
            if cert in text_lower:
                skills.add(cert.title())
        
        return list(skills)
    
    def extract_keywords(self, text):
        """Extract important keywords"""
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                       'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                       'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                       'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
                       'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
        
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        keywords = [w for w in words if w not in common_words]
        
        # Count frequency
        keyword_freq = {}
        for word in keywords:
            keyword_freq[word] = keyword_freq.get(word, 0) + 1
        
        # Return top keywords
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        return [k for k, v in sorted_keywords[:30]]
    
    def analyze_job_description(self, jd_text):
        """Analyze job description"""
        self.jd_skills = self.extract_skills(jd_text)
        self.jd_keywords = self.extract_keywords(jd_text)
        
        # Extract requirements
        jd_lower = jd_text.lower()
        req_patterns = [
            r'required:?\s*(.+?)(?:\n\n|\Z)',
            r'requirements:?\s*(.+?)(?:\n\n|\Z)',
            r'qualifications:?\s*(.+?)(?:\n\n|\Z)',
            r'must have:?\s*(.+?)(?:\n\n|\Z)'
        ]
        
        requirements = []
        for pattern in req_patterns:
            matches = re.findall(pattern, jd_lower, re.DOTALL)
            if matches:
                requirements.extend([r.strip() for r in matches[0].split('\n') if r.strip()])
        
        self.jd_requirements = requirements[:10] if requirements else []
        
        return {
            'skills': self.jd_skills,
            'keywords': self.jd_keywords,
            'requirements': self.jd_requirements
        }
    
    def compare_resume_to_jd(self, resume_text, resume_filename):
        """Detailed comparison of resume against job description"""
        
        # Extract person name
        person_name = self.extract_person_name(resume_text)
        
        # Extract from resume
        resume_skills = self.extract_skills(resume_text)
        resume_keywords = self.extract_keywords(resume_text)
        
        # Skill comparison
        matched_skills = []
        missing_skills = []
        partial_skills = []
        
        for jd_skill in self.jd_skills:
            found = False
            for resume_skill in resume_skills:
                if jd_skill.lower() in resume_skill.lower() or resume_skill.lower() in jd_skill.lower():
                    matched_skills.append(jd_skill)
                    found = True
                    break
            if not found:
                # Check for partial match
                jd_words = set(jd_skill.lower().split())
                resume_words = set(' '.join(resume_skills).lower().split())
                if jd_words & resume_words:
                    partial_skills.append(jd_skill)
                else:
                    missing_skills.append(jd_skill)
        
        # Calculate extra skills (skills in resume but not in JD)
        jd_skills_lower = set([s.lower() for s in self.jd_skills])
        extra_skills = []
        for skill in resume_skills:
            skill_lower = skill.lower()
            # Check if this skill is not in JD and not already matched
            if not any(jd_skill.lower() in skill_lower or skill_lower in jd_skill.lower() 
                      for jd_skill in self.jd_skills):
                extra_skills.append(skill)
        
        # Keyword comparison
        matched_keywords = []
        for jd_kw in self.jd_keywords[:20]:
            if jd_kw in resume_keywords:
                matched_keywords.append(jd_kw)
        
        # Calculate scores
        skill_match_score = len(matched_skills) / len(self.jd_skills) * 100 if self.jd_skills else 0
        keyword_match_score = len(matched_keywords) / min(20, len(self.jd_keywords)) * 100 if self.jd_keywords else 0
        
        # Bonus for extra skills
        extra_skill_bonus = min(len(extra_skills) * 2, 10)
        overall_score = (skill_match_score * 0.6 + keyword_match_score * 0.4) + extra_skill_bonus
        overall_score = min(overall_score, 100)  # Cap at 100
        
        # Extract experience years
        exp_pattern = r'(\d+)\+?\s*(?:years?|yrs?)'
        exp_matches = re.findall(exp_pattern, resume_text.lower())
        years_of_experience = max([int(y) for y in exp_matches]) if exp_matches else 0
        
        # ATS compatibility check
        ats_score = self.calculate_ats_score(resume_text)
        
        return {
            'person_name': person_name,
            'filename': resume_filename,
            'overall_score': round(overall_score, 1),
            'skill_match_score': round(skill_match_score, 1),
            'keyword_match_score': round(keyword_match_score, 1),
            'ats_score': ats_score,
            'matched_skills': matched_skills,
            'partial_skills': partial_skills,
            'missing_skills': missing_skills,
            'extra_skills': extra_skills,
            'matched_keywords': matched_keywords,
            'missing_keywords': [k for k in self.jd_keywords[:20] if k not in matched_keywords],
            'resume_skills': resume_skills,
            'years_experience': years_of_experience,
            'total_jd_skills': len(self.jd_skills),
            'total_jd_keywords': len(self.jd_keywords[:20])
        }
    
    def calculate_ats_score(self, text):
        """Calculate ATS compatibility score"""
        score = 100
        
        # Check for common ATS issues
        if len(text) < 500:
            score -= 20
        
        # Check for proper formatting indicators
        if not any(word in text.lower() for word in ['experience', 'education', 'skills']):
            score -= 15
        
        # Check for contact information
        if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            score -= 10
        
        # Check for phone number
        if not re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text):
            score -= 5
        
        return max(0, score)

# Initialize session state
if 'jd_text' not in st.session_state:
    st.session_state.jd_text = ""
if 'jd_analyzed' not in st.session_state:
    st.session_state.jd_analyzed = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []

# Main app
def main():
    st.markdown('<h1 class="main-header">🎯 Resume Matcher - Detailed Comparison</h1>', unsafe_allow_html=True)
    
    analyzer = ResumeAnalyzer()
    
    # Sidebar - Job Description
    with st.sidebar:
        st.header("📋 Job Description")
        
        jd_input = st.text_area(
            "Paste the job description here",
            value=st.session_state.jd_text,
            height=300,
            placeholder="Paste the complete job description including requirements, skills, and qualifications..."
        )
        
        if st.button("🔍 Analyze Job Description", type="primary"):
            if jd_input.strip():
                st.session_state.jd_text = jd_input
                with st.spinner("Analyzing job description..."):
                    jd_analysis = analyzer.analyze_job_description(jd_input)
                    st.session_state.jd_analyzed = True
                    st.success("Job description analyzed!")
                    
                    st.subheader("Extracted Information:")
                    st.write(f"**Skills Found:** {len(jd_analysis['skills'])}")
                    st.write(f"**Keywords:** {len(jd_analysis['keywords'])}")
                    
                    with st.expander("View Skills"):
                        st.write(", ".join(jd_analysis['skills']))
                    
                    with st.expander("View Keywords"):
                        st.write(", ".join(jd_analysis['keywords'][:20]))
            else:
                st.error("Please enter a job description")
        
        if st.session_state.jd_analyzed:
            st.success("✅ Job Description Ready")
    
    # Main area
    if not st.session_state.jd_analyzed:
        st.info("👈 Please add and analyze a job description first")
        return
    
    # Analyze job description
    analyzer.analyze_job_description(st.session_state.jd_text)
    
    # File upload
    st.header("📤 Upload Resumes")
    uploaded_files = st.file_uploader(
        "Upload multiple resumes (PDF, DOCX, TXT)",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Select multiple files to compare them all at once"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} resume(s) uploaded")
        
        if st.button("🚀 Analyze All Resumes", type="primary"):
            st.session_state.analysis_results = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, file in enumerate(uploaded_files):
                status_text.text(f"Analyzing {file.name}...")
                
                # Extract text
                text = TextExtractor.extract(file)
                
                # Analyze
                result = analyzer.compare_resume_to_jd(text, file.name)
                st.session_state.analysis_results.append(result)
                
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            status_text.text("Analysis complete!")
            st.success(f"✅ Analyzed {len(uploaded_files)} resumes successfully!")
    
    # Display results
    if st.session_state.analysis_results:
        st.header("📊 Comparison Results")
        
        # Sort by overall score
        results = sorted(st.session_state.analysis_results, key=lambda x: x['overall_score'], reverse=True)
        
        # Summary view
        st.subheader("📈 Overview")
        cols = st.columns(min(len(results), 4))
        for idx, (col, result) in enumerate(zip(cols, results)):
            with col:
                medal = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else ""
                st.markdown(f'<div class="candidate-name">{medal} {result["person_name"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="filename-subtitle">{result["filename"][:25]}</div>', unsafe_allow_html=True)
                st.metric("Overall Score", f"{result['overall_score']}%")
                st.metric("Skills Match", f"{result['skill_match_score']}%")
                st.metric("Extra Skills", f"+{len(result['extra_skills'])}")
        
        st.divider()
        
        # Detailed comparison for each resume
        for idx, result in enumerate(results):
            medal = '🥇' if idx == 0 else '🥈' if idx == 1 else '🥉' if idx == 2 else '📄'
            st.markdown(f'<h3>{medal} <span class="candidate-name">{result["person_name"]}</span></h3>', unsafe_allow_html=True)
            st.markdown(f'<div class="filename-subtitle">File: {result["filename"]}</div>', unsafe_allow_html=True)
            st.write("")
            
            # Score cards
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.markdown(f"""
                <div class="score-box" style="background: {'#d4edda' if result['overall_score'] >= 70 else '#fff3cd' if result['overall_score'] >= 50 else '#f8d7da'}">
                    Overall Match<br>{result['overall_score']}%
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="score-box" style="background: {'#d4edda' if result['skill_match_score'] >= 70 else '#fff3cd' if result['skill_match_score'] >= 50 else '#f8d7da'}">
                    Skills Match<br>{result['skill_match_score']}%
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="score-box" style="background: {'#d4edda' if result['keyword_match_score'] >= 70 else '#fff3cd' if result['keyword_match_score'] >= 50 else '#f8d7da'}">
                    Keywords Match<br>{result['keyword_match_score']}%
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="score-box" style="background: {'#d4edda' if result['ats_score'] >= 80 else '#fff3cd' if result['ats_score'] >= 60 else '#f8d7da'}">
                    ATS Score<br>{result['ats_score']}%
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                st.markdown(f"""
                <div class="score-box" style="background: #cfe2ff">
                    Extra Skills<br>+{len(result['extra_skills'])}
                </div>
                """, unsafe_allow_html=True)
            
            # Detailed breakdown
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Skills Comparison", "Extra Skills", "Keywords", "Resume Info", "Recommendations"])
            
            with tab1:
                st.write("### Skills Analysis")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**✅ Matched Skills ({len(result['matched_skills'])})**")
                    if result['matched_skills']:
                        for skill in result['matched_skills']:
                            st.markdown(f'<span class="skill-match">{skill}</span>', unsafe_allow_html=True)
                    else:
                        st.write("No matching skills found")
                
                with col2:
                    st.write(f"**⚠️ Partial Match ({len(result['partial_skills'])})**")
                    if result['partial_skills']:
                        for skill in result['partial_skills']:
                            st.markdown(f'<span class="skill-partial">{skill}</span>', unsafe_allow_html=True)
                    else:
                        st.write("None")
                
                with col3:
                    st.write(f"**❌ Missing Skills ({len(result['missing_skills'])})**")
                    if result['missing_skills']:
                        for skill in result['missing_skills']:
                            st.markdown(f'<span class="skill-missing">{skill}</span>', unsafe_allow_html=True)
                    else:
                        st.write("None")
                
                st.write("---")
                st.write(f"**📚 All Skills in Resume ({len(result['resume_skills'])})**")
                st.write(", ".join(result['resume_skills']))
            
            with tab2:
                st.write("### 🌟 Additional Skills Beyond Job Requirements")
                if result['extra_skills']:
                    st.success(f"This candidate has **{len(result['extra_skills'])} additional valuable skills** not mentioned in the job description!")
                    st.write("")
                    st.write("**Extra Skills:**")
                    for skill in result['extra_skills']:
                        st.markdown(f'<span class="skill-extra">➕ {skill}</span>', unsafe_allow_html=True)
                    st.write("")
                    st.info("💡 These extra skills could bring additional value to the role and team.")
                else:
                    st.write("No additional skills beyond job requirements found.")
                    st.info("This candidate's skills closely match the job requirements without additional expertise.")
            
            with tab3:
                st.write("### Keyword Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**✅ Matched Keywords ({len(result['matched_keywords'])}/{result['total_jd_keywords']})**")
                    if result['matched_keywords']:
                        st.write(", ".join(result['matched_keywords']))
                    else:
                        st.write("No matching keywords")
                
                with col2:
                    st.write(f"**❌ Missing Keywords ({len(result['missing_keywords'])})**")
                    if result['missing_keywords']:
                        st.write(", ".join(result['missing_keywords'][:10]))
                    else:
                        st.write("None")
            
            with tab4:
                st.write("### Resume Information")
                st.write(f"**Candidate Name:** {result['person_name']}")
                st.write(f"**Years of Experience:** {result['years_experience']} years")
                st.write(f"**ATS Compatibility:** {result['ats_score']}%")
                st.write(f"**Total Skills Found:** {len(result['resume_skills'])}")
                st.write(f"**Matched Skills:** {len(result['matched_skills'])}")
                st.write(f"**Extra Skills:** {len(result['extra_skills'])}")
            
            with tab5:
                st.write("### Recommendations")
                
                if result['overall_score'] >= 70:
                    st.success(f"✅ **Strong candidate!** {result['person_name']} is an excellent match for the position.")
                    if result['extra_skills']:
                        st.info(f"➕ Bonus: Has {len(result['extra_skills'])} additional skills that could add value!")
                elif result['overall_score'] >= 50:
                    st.warning(f"⚠️ **Moderate match.** {result['person_name']} meets some requirements but review missing skills.")
                else:
                    st.error(f"❌ **Low match.** {result['person_name']} may not meet the core requirements.")
                
                if result['missing_skills']:
                    st.write("**Skills to Highlight or Acquire:**")
                    for skill in result['missing_skills'][:5]:
                        st.write(f"- {skill}")
                
                if result['extra_skills'] and result['overall_score'] >= 60:
                    st.write("**Value-Add Skills:**")
                    for skill in result['extra_skills'][:5]:
                        st.write(f"+ {skill}")
                
                if result['ats_score'] < 80:
                    st.write("**ATS Improvement Suggestions:**")
                    st.write("- Ensure clear section headers (Experience, Education, Skills)")
                    st.write("- Include contact information prominently")
                    st.write("- Use standard formatting without tables or graphics")
            
            st.divider()
        
        # Export option
        if st.button("📥 Export Comparison Report"):
            report = {
                'analysis_date': datetime.now().isoformat(),
                'job_description_summary': {
                    'total_skills': len(analyzer.jd_skills),
                    'total_keywords': len(analyzer.jd_keywords)
                },
                'resumes_analyzed': len(results),
                'detailed_results': results
            }
            
            st.download_button(
                label="Download JSON Report",
                data=json.dumps(report, indent=2),
                file_name=f"resume_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()