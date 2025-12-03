import os
import sys
from pathlib import Path

from utils.logger import Logger
from utils.file_loader import FileLoader
from extraction.pdf_extractor import PDFExtractor
from extraction.docx_extractor import DOCXExtractor
from extraction.text_cleaner import TextCleaner
from processing.skill_extractor import SkillExtractor
from processing.jd_skill_extractor import JDSkillExtractor
from processing.embedder import Embedder
from processing.similarity_matcher import SimilarityMatcher
from scoring.match_scorer import MatchScorer
from scoring.experience_scorer import ExperienceScorer
from scoring.summary_generator import SummaryGenerator

class ResumeAnalyzer:
    """Main resume analyzer application."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize analyzer with configuration."""
        self.logger = Logger()
        self.logger.info("Initializing Resume Analyzer...")
        
        self.config = FileLoader.load_yaml(config_path)
        self.skills_dict = FileLoader.load_json(
            self.config['paths']['skills_dict']
        )
        
        self._setup_extractors()
        self._setup_processors()
        self._setup_scorers()
        
        self.logger.info("Resume Analyzer initialized successfully!")
    
    def _setup_extractors(self):
        """Setup extraction components."""
        self.pdf_extractor = PDFExtractor()
        self.docx_extractor = DOCXExtractor()
        self.text_cleaner = TextCleaner(
            remove_stopwords=self.config['extraction']['remove_stopwords'],
            lowercase=self.config['extraction']['lowercase']
        )
    
    def _setup_processors(self):
        """Setup processing components."""
        self.skill_extractor = SkillExtractor(
            self.skills_dict,
            self.config['models']['spacy_model']
        )
        self.jd_extractor = JDSkillExtractor(self.skills_dict)
        self.embedder = Embedder(self.config['models']['sentence_transformer'])
        self.matcher = SimilarityMatcher(
            self.config['scoring']['thresholds']['skill_fuzzy_match']
        )
    
    def _setup_scorers(self):
        """Setup scoring components."""
        self.scorer = MatchScorer(self.config['scoring']['weights'])
        self.exp_scorer = ExperienceScorer()
        self.summary_gen = SummaryGenerator()
    
    def extract_text(self, filepath: str) -> str:
        """Extract text from resume file."""
        self.logger.info(f"Extracting text from: {filepath}")
        
        file_type = FileLoader.detect_file_type(filepath)
        
        if file_type == 'pdf':
            text = self.pdf_extractor.extract(filepath)
        elif file_type == 'docx':
            text = self.docx_extractor.extract(filepath)
        elif file_type == 'txt':
            text = FileLoader.read_text_file(filepath)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        self.logger.info(f"Extracted {len(text)} characters")
        return text
    
    def analyze(self, resume_path: str, jd_text: str, job_title: str = "Unknown") -> dict:
        """
        Perform complete resume analysis.
        
        Args:
            resume_path: Path to resume file
            jd_text: Job description text
            job_title: Job title for the position
            
        Returns:
            Complete analysis results
        """
        self.logger.info("=" * 70)
        self.logger.info("Starting Resume Analysis")
        self.logger.info("=" * 70)
        
        resume_text = self.extract_text(resume_path)
        
        self.logger.info("Cleaning text...")
        resume_clean = self.text_cleaner.clean(resume_text)
        jd_clean = self.text_cleaner.clean(jd_text)
        
        self.logger.info("Extracting skills from resume...")
        resume_skills = self.skill_extractor.extract(resume_text)
        resume_experience = self.skill_extractor.extract_years_of_experience(resume_text)
        
        self.logger.info("Extracting requirements from job description...")
        jd_analysis = self.jd_extractor.extract(jd_text)
        jd_skills = jd_analysis['required_skills']
        jd_experience = jd_analysis['experience_requirement']
        
        self.logger.info("Matching skills...")
        skill_matching = self.matcher.match_skills(resume_skills, jd_skills)
        
        self.logger.info("Calculating semantic similarity...")
        semantic_similarity = self.embedder.calculate_similarity(
            resume_clean[:5000],
            jd_clean[:5000]
        )
        
        self.logger.info("Scoring match quality...")
        skill_score = self.scorer.calculate_skill_match_score(
            len(skill_matching['matched_exact']),
            skill_matching['total_required'],
            len(skill_matching['matched_fuzzy'])
        )
        
        semantic_score = self.scorer.calculate_semantic_score(semantic_similarity)
        
        experience_score = self.exp_scorer.calculate_experience_score(
            resume_experience,
            jd_experience
        )
        
        qualification_score = 70.0
        
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
        
        results = {
            'resume_file': os.path.basename(resume_path),
            'job_title': job_title,
            'resume_skills': resume_skills,
            'jd_analysis': jd_analysis,
            'skill_matching': skill_matching,
            'semantic_similarity': semantic_similarity,
            'experience_analysis': experience_analysis,
            'final_score': final_score
        }
        
        self.logger.info("Generating report...")
        report = self.summary_gen.generate_report(results)
        
        self.logger.info("=" * 70)
        self.logger.info(f"Analysis Complete! Final Score: {final_score['final_score']}/100")
        self.logger.info("=" * 70)
        
        return report
    
    def save_report(self, report: dict, output_path: str = None):
        """Save analysis report."""
        if output_path is None:
            output_dir = self.config['paths']['output_reports']
            FileLoader.ensure_directory(output_dir)
            timestamp = report['metadata']['generated_at'].replace(':', '-').replace(' ', '_')
            output_path = f"{output_dir}/report_{timestamp}.json"
        
        FileLoader.save_json(report, output_path)
        self.logger.info(f"Report saved to: {output_path}")
        
        text_path = output_path.replace('.json', '.txt')
        text_report = self.summary_gen.generate_text_report(report)
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text_report)
        self.logger.info(f"Text report saved to: {text_path}")
        
        return output_path

def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) < 3:
        print("Usage: python main.py <resume_path> <jd_path> [job_title]")
        print("Example: python main.py input/resumes/resume.pdf input/job_descriptions/jd.txt 'Software Engineer'")
        sys.exit(1)
    
    resume_path = sys.argv[1]
    jd_path = sys.argv[2]
    job_title = sys.argv[3] if len(sys.argv) > 3 else "Unknown Position"
    
    if not os.path.exists(resume_path):
        print(f"Error: Resume file not found: {resume_path}")
        sys.exit(1)
    
    if not os.path.exists(jd_path):
        print(f"Error: Job description file not found: {jd_path}")
        sys.exit(1)
    
    analyzer = ResumeAnalyzer()
    
    jd_text = FileLoader.read_text_file(jd_path)
    
    report = analyzer.analyze(resume_path, jd_text, job_title)
    
    output_path = analyzer.save_report(report)
    
    print("\n" + "=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"Final Score: {report['overall_score']['final_score']}/100")
    print(f"Rating: {report['overall_score']['rating']}")
    print(f"\nReport saved to: {output_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()