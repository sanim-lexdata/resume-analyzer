"""
Enhanced Resume Analyzer with HuggingFace Transformers and ESCO/O*NET Integration
Complete fixed version with proper error handling
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import Logger
from utils.file_loader import FileLoader
from utils.esco_fetcher import ESCOFetcher
from utils.onet_fetcher import ONETFetcher
from extraction.pdf_extractor import PDFExtractor
from extraction.docx_extractor import DOCXExtractor
from extraction.text_cleaner import TextCleaner
from processing.skill_extractor import SkillExtractor
from processing.hf_skill_extractor import HFSkillExtractor
from processing.jd_skill_extractor import JDSkillExtractor
from processing.embedder import Embedder
from processing.similarity_matcher import SimilarityMatcher
from scoring.match_scorer import MatchScorer
from scoring.experience_scorer import ExperienceScorer
from scoring.summary_generator import SummaryGenerator


class EnhancedResumeAnalyzer:
    """Enhanced Resume Analyzer with HuggingFace and ESCO/O*NET integration."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Enhanced Resume Analyzer.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = Logger(__name__)
        self.logger.info("Initializing Enhanced Resume Analyzer with HF & ESCO/O*NET...")
        
        # Load configuration
        self.config = self.load_config(config_path)
        
        # Initialize extractors
        self.pdf_extractor = PDFExtractor()
        self.docx_extractor = DOCXExtractor()
        self.text_cleaner = TextCleaner(
            remove_stopwords=self.config.get('extraction', {}).get('remove_stopwords', False),
            lowercase=self.config.get('extraction', {}).get('lowercase', False)
        )
        
        # Load skill taxonomies
        self.logger.info("Loading skill taxonomies...")
        self.skills_dict = self.load_skills_dictionary()
        self.esco_skills = self.load_esco_skills()
        self.onet_skills = self.load_onet_skills()
        
        # Merge all skill sources
        self.all_skills = self.merge_skill_sources()
        self.logger.info(f"Total skill categories: {len(self.all_skills)}")
        
        # Initialize processors
        self.skill_extractor = SkillExtractor(self.all_skills)
        self.hf_extractor = HFSkillExtractor()
        self.jd_extractor = JDSkillExtractor(self.all_skills)
        self.embedder = Embedder()
        self.matcher = SimilarityMatcher()
        
        # Initialize scorers
        self.scorer = MatchScorer()
        self.exp_scorer = ExperienceScorer()
        self.summary_gen = SummaryGenerator()
        
        self.logger.info("Enhanced Resume Analyzer initialized successfully!")
    
    def load_config(self, config_path: str = None) -> dict:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = "config/settings.yaml"
        
        try:
            import yaml
            if Path(config_path).exists():
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                self.logger.warning(f"Config file not found: {config_path}, using defaults")
                return self.get_default_config()
        except Exception as e:
            self.logger.warning(f"Error loading config: {e}, using defaults")
            return self.get_default_config()
    
    def get_default_config(self) -> dict:
        """Get default configuration."""
        return {
            'extraction': {
                'remove_stopwords': False,
                'lowercase': False
            },
            'matching': {
                'fuzzy_threshold': 85,
                'semantic_threshold': 0.7
            },
            'scoring': {
                'weights': {
                    'skills': 0.4,
                    'semantic': 0.3,
                    'experience': 0.2,
                    'qualifications': 0.1
                }
            }
        }
    
    def load_skills_dictionary(self) -> dict:
        """Load custom skills dictionary."""
        skills_path = "data/skills_dictionary.json"
        try:
            if Path(skills_path).exists():
                import json
                with open(skills_path, 'r') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"Skills dictionary not found: {skills_path}")
                return self.get_default_skills()
        except Exception as e:
            self.logger.warning(f"Error loading skills dictionary: {e}")
            return self.get_default_skills()
    
    def get_default_skills(self) -> dict:
        """Get default skills dictionary."""
        return {
            "programming_languages": ["Python", "Java", "JavaScript", "C++", "C#", "Ruby", "Go", "Rust", "PHP", "Swift"],
            "web_frameworks": ["Django", "Flask", "FastAPI", "React", "Vue.js", "Angular", "Node.js", "Express.js", "Spring Boot"],
            "databases": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra", "Oracle", "SQL Server"],
            "cloud_platforms": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "CloudFormation"],
            "devops_tools": ["Jenkins", "GitLab CI", "GitHub Actions", "CircleCI", "Travis CI", "Ansible", "Chef", "Puppet"],
            "data_science": ["Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Keras", "Matplotlib", "Seaborn"],
            "soft_skills": ["Leadership", "Communication", "Problem Solving", "Teamwork", "Agile", "Scrum"]
        }
    
    def load_esco_skills(self) -> list:
        """Load ESCO skills taxonomy."""
        try:
            fetcher = ESCOFetcher()
            skills = fetcher.fetch_skills()
            self.logger.info(f"Loaded {len(skills)} ESCO skills")
            return skills
        except Exception as e:
            self.logger.warning(f"Could not load ESCO skills: {e}")
            return []
    
    def load_onet_skills(self) -> list:
        """Load O*NET skills taxonomy."""
        try:
            fetcher = ONETFetcher()
            skills = fetcher.fetch_skills()
            self.logger.info(f"Loaded {len(skills)} O*NET skills")
            return skills
        except Exception as e:
            self.logger.warning(f"Could not load O*NET skills: {e}")
            return []
    
    def merge_skill_sources(self) -> dict:
        """Merge skills from all sources."""
        merged = {}
        
        # Add custom dictionary skills
        for category, skills in self.skills_dict.items():
            merged[category] = set(skills)
        
        # Add ESCO skills
        if self.esco_skills:
            if 'esco_skills' not in merged:
                merged['esco_skills'] = set()
            for skill in self.esco_skills:
                merged['esco_skills'].add(skill)
        
        # Add O*NET skills
        if self.onet_skills:
            if 'onet_skills' not in merged:
                merged['onet_skills'] = set()
            for skill in self.onet_skills:
                merged['onet_skills'].add(skill)
        
        # Convert sets back to lists
        return {k: list(v) for k, v in merged.items()}
    
    def extract_text(self, filepath: str) -> dict:
        """
        Extract and clean text from resume file.
        
        Args:
            filepath: Path to resume file
            
        Returns:
            dict with 'text', 'contact', 'sections'
        """
        self.logger.info(f"Extracting text from: {filepath}")
        
        try:
            # Determine file type and extract
            file_ext = Path(filepath).suffix.lower()
            
            if file_ext == '.pdf':
                raw_text = self.pdf_extractor.extract(filepath)
            elif file_ext in ['.docx', '.doc']:
                raw_text = self.docx_extractor.extract(filepath)
            elif file_ext == '.txt':
                raw_text = FileLoader.read_text_file(filepath)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            # Validate extraction result
            if raw_text is None:
                self.logger.error(f"Text extraction returned None for {filepath}")
                raise ValueError(
                    f"Could not extract text from {filepath}. "
                    f"The file might be:\n"
                    f"  • Scanned/image-based PDF (use OCR or convert to text)\n"
                    f"  • Corrupted or password-protected\n"
                    f"  • Empty file\n"
                    f"Please try using a .txt or .docx file instead."
                )
            
            # Convert to string and validate
            raw_text = str(raw_text).strip()
            
            if not raw_text or len(raw_text) < 50:
                self.logger.error(f"Extracted text is too short: {len(raw_text)} chars")
                raise ValueError(
                    f"Extracted text is too short ({len(raw_text)} characters). "
                    f"Please ensure the file contains readable text content."
                )
            
            self.logger.info(f"Extracted {len(raw_text)} characters")
            
            # Clean the text
            self.logger.info("Cleaning text...")
            cleaned_text = self.text_cleaner.clean(raw_text)
            
            if not cleaned_text or len(cleaned_text) < 30:
                self.logger.warning("Cleaned text is very short, using raw text")
                cleaned_text = raw_text
            
            self.logger.info(f"Cleaned to {len(cleaned_text)} characters")
            
            # Extract contact info
            contact_info = self._extract_contact_info(raw_text)
            
            # Parse sections
            sections = self._parse_sections(cleaned_text)
            
            result = {
                'text': cleaned_text,
                'raw_text': raw_text,
                'contact': contact_info,
                'sections': sections
            }
            
            return result
            
        except FileNotFoundError:
            self.logger.error(f"File not found: {filepath}")
            raise
        except Exception as e:
            self.logger.error(f"Error extracting text: {e}")
            raise
    
    def _extract_contact_info(self, text: str) -> dict:
        """Extract contact information from text."""
        import re
        
        contact = {
            'email': None,
            'phone': None,
            'linkedin': None,
            'github': None
        }
        
        # Email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if email_match:
            contact['email'] = email_match.group()
        
        # Phone
        phone_match = re.search(r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b', text)
        if phone_match:
            contact['phone'] = phone_match.group()
        
        # LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
        if linkedin_match:
            contact['linkedin'] = linkedin_match.group()
        
        # GitHub
        github_match = re.search(r'github\.com/[\w-]+', text, re.IGNORECASE)
        if github_match:
            contact['github'] = github_match.group()
        
        return contact
    
    def _parse_sections(self, text: str) -> dict:
        """Parse resume into sections."""
        sections = {
            'summary': '',
            'experience': '',
            'education': '',
            'skills': '',
            'projects': ''
        }
        
        # Simple section parsing based on common headers
        import re
        
        # Find section headers
        patterns = {
            'summary': r'(?:SUMMARY|PROFILE|ABOUT|OBJECTIVE)',
            'experience': r'(?:EXPERIENCE|WORK HISTORY|EMPLOYMENT)',
            'education': r'(?:EDUCATION|ACADEMIC)',
            'skills': r'(?:SKILLS|TECHNICAL SKILLS|COMPETENCIES)',
            'projects': r'(?:PROJECTS|PORTFOLIO)'
        }
        
        for section, pattern in patterns.items():
            match = re.search(f'{pattern}.*?(?=(?:{"|".join(patterns.values())})|$)', 
                            text, re.IGNORECASE | re.DOTALL)
            if match:
                sections[section] = match.group()
        
        return sections
    
    def analyze(self, resume_path: str, jd_text: str, job_title: str = None) -> dict:
        """
        Perform comprehensive resume analysis.
        
        Args:
            resume_path: Path to resume file
            jd_text: Job description text
            job_title: Optional job title
            
        Returns:
            Comprehensive analysis report
        """
        self.logger.info("="*70)
        self.logger.info("Starting Enhanced Resume Analysis")
        self.logger.info("="*70)
        
        try:
            # Extract and clean resume text
            resume_data = self.extract_text(resume_path)
            resume_text = resume_data['text']
            
            # Clean job description
            self.logger.info("Cleaning job description...")
            jd_text_cleaned = self.text_cleaner.clean(jd_text)
            
            # Traditional skill extraction
            self.logger.info("Extracting skills with traditional NER...")
            traditional_skills = self.skill_extractor.extract(resume_text)
            resume_experience_raw = self.skill_extractor.extract_years_of_experience(resume_text)
            
            # Convert experience to integer if it's a dict (FIX FOR DICT ISSUE)
            if isinstance(resume_experience_raw, dict):
                resume_experience = resume_experience_raw.get('years', None)
            elif isinstance(resume_experience_raw, (int, float)):
                resume_experience = int(resume_experience_raw)
            else:
                resume_experience = None
            
            # HuggingFace skill extraction
            self.logger.info("Extracting skills with HuggingFace Transformers...")
            try:
                hf_skills = self.hf_extractor.extract(resume_text)
            except Exception as e:
                self.logger.warning(f"HF extraction failed: {e}")
                hf_skills = {'skills': [], 'entities': []}
            
            # Merge traditional and HF skills
            all_resume_skills = self._merge_skills(traditional_skills, hf_skills)
            
            # Extract job description requirements
            self.logger.info("Extracting requirements from job description...")
            jd_analysis = self.jd_extractor.extract(jd_text_cleaned)
            required_skills = jd_analysis['required_skills']
            
            # Convert JD experience to integer if it's a dict (FIX FOR DICT ISSUE)
            jd_experience_raw = jd_analysis['experience_requirement']
            if isinstance(jd_experience_raw, dict):
                jd_experience = jd_experience_raw.get('years', None)
            elif isinstance(jd_experience_raw, (int, float)):
                jd_experience = int(jd_experience_raw)
            else:
                jd_experience = None
            
            # Skill matching
            self.logger.info("Matching skills...")
            skill_matching = self.matcher.match_skills(
                all_resume_skills['skills'],
                required_skills,
                threshold=self.config.get('matching', {}).get('fuzzy_threshold', 85)
            )
            
            # Semantic similarity
            self.logger.info("Calculating semantic similarity...")
            semantic_similarity = self.embedder.calculate_similarity(
                resume_text,
                jd_text_cleaned
            )
            
            # Semantic skill matching
            self.logger.info("Performing semantic skill matching...")
            semantic_skill_match = self.embedder.semantic_skill_match(
                all_resume_skills['skills'],
                required_skills,
                threshold=self.config.get('matching', {}).get('semantic_threshold', 0.7)
            )
            
            # Calculate scores
            self.logger.info("Scoring match quality...")
            
            # Combine exact + fuzzy + semantic matches
            total_matched = (
                len(skill_matching['matched_exact']) +
                len(skill_matching['matched_fuzzy']) +
                len(semantic_skill_match['matched'])
            )
            
            skill_score = self.scorer.calculate_skill_match_score(
                len(skill_matching['matched_exact']),
                skill_matching['total_required'],
                len(skill_matching['matched_fuzzy']) + len(semantic_skill_match['matched'])
            )
            
            semantic_score = self.scorer.calculate_semantic_score(semantic_similarity)
            
            experience_score = self.exp_scorer.calculate_experience_score(
                resume_experience,
                jd_experience
            )
            
            qualification_score = 70.0  # Placeholder
            
            final_score = self.scorer.calculate_final_score(
                skill_score,
                semantic_score,
                experience_score,
                qualification_score
            )
            
            experience_analysis = self.exp_scorer.analyze_experience_gap(
                resume_experience,
                jd_experience
            )
            
            # Generate comprehensive report
            self.logger.info("Generating comprehensive report...")
            report = self.summary_gen.generate_report(
                final_score=final_score,
                skill_score=skill_score,
                semantic_score=semantic_score,
                experience_score=experience_score,
                qualification_score=qualification_score,
                matched_skills_exact=skill_matching['matched_exact'],
                matched_skills_fuzzy=skill_matching['matched_fuzzy'],
                matched_skills_semantic=semantic_skill_match['matched'],
                missing_skills=skill_matching['missing'],
                extra_skills=skill_matching['extra'],
                semantic_similarity=semantic_similarity,
                experience_analysis=experience_analysis,
                resume_text=resume_text,
                jd_text=jd_text_cleaned,
                job_title=job_title,
                contact_info=resume_data['contact']
            )
            
            # Save report
            output_dir = Path("output/reports")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            report_filename = f"enhanced_report_{timestamp}.json"
            report_path = output_dir / report_filename
            
            import json
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Report saved to: {report_path}")
            
            # Also save text report
            text_report_path = output_dir / f"enhanced_report_{timestamp}.txt"
            self._save_text_report(report, text_report_path)
            
            self.logger.info("="*70)
            self.logger.info(f"Analysis Complete! Final Score: {final_score:.1f}/100")
            self.logger.info(f"Skills extracted - Traditional: {len(traditional_skills)}, HF: {len(hf_skills.get('skills', []))}, Merged: {len(all_resume_skills['skills'])}")
            self.logger.info("="*70)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _merge_skills(self, traditional: list, hf: dict) -> dict:
        """Merge skills from traditional and HF extraction."""
        merged_skills = set(traditional)
        
        # Add HF skills
        if 'skills' in hf:
            merged_skills.update(hf['skills'])
        
        return {
            'skills': list(merged_skills),
            'traditional_count': len(traditional),
            'hf_count': len(hf.get('skills', [])),
            'total_count': len(merged_skills)
        }
    
    def _save_text_report(self, report: dict, filepath: Path):
        """Save a human-readable text report."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("ENHANCED RESUME ANALYSIS REPORT\n")
            f.write("="*70 + "\n\n")
            
            # Overall score
            overall = report.get('overall_score', {})
            f.write(f"Final Score: {overall.get('final_score', 0):.1f}/100\n")
            f.write(f"Rating: {overall.get('rating', 'N/A')}\n\n")
            
            # Breakdown
            breakdown = overall.get('breakdown', {})
            f.write("Score Breakdown:\n")
            f.write(f"  • Skill Match: {breakdown.get('skill_score', 0):.1f}/100\n")
            f.write(f"  • Semantic Similarity: {breakdown.get('semantic_score', 0):.1f}/100\n")
            f.write(f"  • Experience: {breakdown.get('experience_score', 0):.1f}/100\n")
            f.write(f"  • Qualifications: {breakdown.get('qualification_score', 0):.1f}/100\n\n")
            
            # Skills analysis
            skills = report.get('skills_analysis', {})
            f.write("Skills Analysis:\n")
            f.write(f"  Matched (Exact): {len(skills.get('matched_exact', []))}\n")
            f.write(f"  Matched (Fuzzy): {len(skills.get('matched_fuzzy', []))}\n")
            f.write(f"  Matched (Semantic): {len(skills.get('matched_semantic', []))}\n")
            f.write(f"  Missing: {len(skills.get('missing', []))}\n")
            f.write(f"  Extra: {len(skills.get('extra', []))}\n\n")
            
            # Experience
            exp = report.get('experience_analysis', {})
            f.write("Experience Analysis:\n")
            f.write(f"  {exp.get('message', 'N/A')}\n")
            f.write(f"  Recommendation: {exp.get('recommendation', 'N/A')}\n\n")
            
            # Recommendations
            recs = report.get('recommendations', [])
            if recs:
                f.write("Recommendations:\n")
                for i, rec in enumerate(recs, 1):
                    f.write(f"  {i}. {rec}\n")
            
            f.write("\n" + "="*70 + "\n")
        
        self.logger.info(f"Text report saved to: {filepath}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Resume Analyzer')
    parser.add_argument('resume', help='Path to resume file (PDF/DOCX/TXT)')
    parser.add_argument('jd', help='Path to job description file (TXT)')
    parser.add_argument('job_title', nargs='?', default='', help='Job title (optional)')
    parser.add_argument('--config', help='Path to config file', default=None)
    
    args = parser.parse_args()
    
    try:
        print("\n🚀 Initializing Enhanced Resume Analyzer...")
        analyzer = EnhancedResumeAnalyzer(config_path=args.config)
        
        # Load job description
        print(f"📄 Loading job description from: {args.jd}")
        jd_text = FileLoader.read_text_file(args.jd)
        
        # Analyze
        print(f"🔍 Analyzing resume: {args.resume}\n")
        report = analyzer.analyze(args.resume, jd_text, args.job_title)
        
        # Print summary
        print("\n" + "=" * 70)
        print("✅ ENHANCED ANALYSIS SUMMARY")
        print("=" * 70)
        
        overall = report.get('overall_score', {})
        breakdown = overall.get('breakdown', {})
        
        print(f"Final Score: {overall.get('final_score', 0):.1f}/100")
        print(f"Rating: {overall.get('rating', 'N/A')}")
        print(f"\n📊 Breakdown:")
        print(f"  • Skill Match: {breakdown.get('skill_score', 0):.1f}/100")
        print(f"  • Semantic Similarity: {breakdown.get('semantic_score', 0):.1f}/100")
        print(f"  • Experience: {breakdown.get('experience_score', 0):.1f}/100")
        print(f"  • Qualifications: {breakdown.get('qualification_score', 0):.1f}/100")
        
        print(f"\n🎯 Skill Sources Used:")
        print(f"  • Custom Dictionary: ✓")
        print(f"  • ESCO Taxonomy: {'✓' if analyzer.esco_skills else '✗'}")
        print(f"  • O*NET Database: {'✓' if analyzer.onet_skills else '✗'}")
        print(f"  • HuggingFace Transformers: ✓")
        
        skills = report.get('skills_analysis', {})
        print(f"\n💡 Skills Summary:")
        print(f"  • Matched: {len(skills.get('matched_exact', [])) + len(skills.get('matched_fuzzy', [])) + len(skills.get('matched_semantic', []))}")
        print(f"  • Missing: {len(skills.get('missing', []))}")
        print(f"  • Bonus: {len(skills.get('extra', []))}")
        
        # Show missing skills if any
        missing = skills.get('missing', [])
        if missing:
            print(f"\n❌ Key Missing Skills (showing up to 10):")
            for skill in missing[:10]:
                print(f"  • {skill}")
        
        print("\n💾 Report saved to: output/reports/")
        print("=" * 70 + "\n")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: File not found - {e}")
        print("   Please check that the file paths are correct.")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()