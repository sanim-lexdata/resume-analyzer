"""
Experience Scorer Module
Analyzes and scores candidate experience against job requirements.
"""

import re
from typing import Dict, List, Tuple, Optional


class ExperienceScorer:
    """
    Scores candidate experience based on job requirements.
    """
    
    def __init__(self):
        """Initialize experience scorer."""
        self.experience_keywords = [
            'years of experience', 'years experience', 'year of experience',
            'yrs experience', 'years', 'year', 'yrs', 'yr',
            'experience in', 'worked as', 'working as',
            'senior', 'junior', 'mid-level', 'entry-level',
            'lead', 'principal', 'staff', 'architect'
        ]
        
        self.seniority_levels = {
            'entry-level': (0, 2),
            'junior': (0, 2),
            'mid-level': (2, 5),
            'intermediate': (2, 5),
            'senior': (5, 10),
            'lead': (7, 15),
            'principal': (10, 20),
            'staff': (8, 15),
            'architect': (10, 20),
            'director': (10, 20),
            'manager': (5, 15)
        }
    
    def extract_years_from_text(self, text: str) -> Optional[int]:
        """
        Extract years of experience from text.
        
        Args:
            text: Text to extract years from
            
        Returns:
            Number of years or None if not found
        """
        if not text:
            return None
        
        text = text.lower()
        
        # Pattern 1: "X years of experience" or "X+ years"
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience',
            r'(\d+)\+?\s*(?:years?|yrs?)',
            r'experience:\s*(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:in|with)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Return the maximum years found
                return max(int(m) for m in matches)
        
        # Pattern 2: Check for seniority levels
        for level, (min_years, max_years) in self.seniority_levels.items():
            if level in text:
                # Return middle of range
                return (min_years + max_years) // 2
        
        return None
    
    def calculate_experience_score(
        self, 
        candidate_years: Optional[int], 
        required_years: Optional[int]
    ) -> float:
        """
        Calculate experience match score.
        
        Args:
            candidate_years: Candidate's years of experience
            required_years: Required years of experience
            
        Returns:
            Score from 0-100
        """
        # If no requirement specified, give neutral score
        if required_years is None or required_years == 0:
            return 70.0
        
        # If candidate experience not found, give lower score
        if candidate_years is None:
            return 50.0
        
        # Calculate score based on experience match
        if candidate_years >= required_years:
            # Candidate meets or exceeds requirement
            if candidate_years <= required_years * 1.5:
                # Ideal range (100%)
                return 100.0
            elif candidate_years <= required_years * 2:
                # Slightly overqualified (95%)
                return 95.0
            else:
                # Very overqualified (may be overqualified issue)
                return 85.0
        else:
            # Candidate has less experience than required
            ratio = candidate_years / required_years
            
            if ratio >= 0.8:
                # 80-99% of requirement (80-90 score)
                return 80.0 + (ratio - 0.8) * 50
            elif ratio >= 0.6:
                # 60-79% of requirement (60-79 score)
                return 60.0 + (ratio - 0.6) * 100
            elif ratio >= 0.4:
                # 40-59% of requirement (40-59 score)
                return 40.0 + (ratio - 0.4) * 100
            else:
                # Less than 40% of requirement (0-39 score)
                return ratio * 100
    
    def analyze_experience_gap(
        self,
        candidate_years: Optional[int],
        required_years: Optional[int]
    ) -> Dict:
        """
        Analyze the gap between candidate and required experience.
        
        Args:
            candidate_years: Candidate's years of experience
            required_years: Required years of experience
            
        Returns:
            Dictionary with gap analysis
        """
        analysis = {
            'candidate_experience': candidate_years if candidate_years else 0,
            'required_experience': required_years if required_years else 0,
            'gap': 0,
            'gap_percentage': 0.0,
            'status': 'unknown',
            'message': '',
            'recommendation': ''
        }
        
        if required_years is None or required_years == 0:
            analysis['status'] = 'no_requirement'
            analysis['message'] = 'No specific experience requirement mentioned'
            analysis['recommendation'] = 'Highlight relevant skills and projects'
            return analysis
        
        if candidate_years is None:
            analysis['status'] = 'not_found'
            analysis['message'] = 'Experience not clearly mentioned in resume'
            analysis['recommendation'] = 'Add clear experience timeline to resume'
            return analysis
        
        gap = required_years - candidate_years
        analysis['gap'] = gap
        
        if candidate_years > 0:
            analysis['gap_percentage'] = (gap / required_years) * 100
        
        if candidate_years >= required_years:
            if candidate_years <= required_years * 1.5:
                analysis['status'] = 'meets_requirement'
                analysis['message'] = f'Candidate meets experience requirement ({candidate_years} years)'
                analysis['recommendation'] = 'Strong match - emphasize relevant achievements'
            elif candidate_years <= required_years * 2:
                analysis['status'] = 'exceeds_requirement'
                analysis['message'] = f'Candidate exceeds requirement ({candidate_years} vs {required_years} years)'
                analysis['recommendation'] = 'Highlight leadership and mentoring capabilities'
            else:
                analysis['status'] = 'highly_experienced'
                analysis['message'] = f'Candidate is significantly more experienced ({candidate_years} vs {required_years} years)'
                analysis['recommendation'] = 'May be overqualified - emphasize continued growth motivation'
        else:
            ratio = candidate_years / required_years if required_years > 0 else 0
            
            if ratio >= 0.8:
                analysis['status'] = 'close_match'
                analysis['message'] = f'Candidate is close to requirement ({candidate_years} vs {required_years} years, {abs(gap)} year gap)'
                analysis['recommendation'] = 'Emphasize rapid learning and relevant project impact'
            elif ratio >= 0.6:
                analysis['status'] = 'moderate_gap'
                analysis['message'] = f'Moderate experience gap ({candidate_years} vs {required_years} years, {abs(gap)} year gap)'
                analysis['recommendation'] = 'Highlight transferable skills and intensive learning experiences'
            elif ratio >= 0.4:
                analysis['status'] = 'significant_gap'
                analysis['message'] = f'Significant experience gap ({candidate_years} vs {required_years} years, {abs(gap)} year gap)'
                analysis['recommendation'] = 'Focus on relevant certifications, bootcamps, and project portfolio'
            else:
                analysis['status'] = 'large_gap'
                analysis['message'] = f'Large experience gap ({candidate_years} vs {required_years} years, {abs(gap)} year gap)'
                analysis['recommendation'] = 'Consider entry-level positions or intensive training programs'
        
        return analysis
    
    def extract_work_history(self, text: str) -> List[Dict]:
        """
        Extract work history entries from resume text.
        
        Args:
            text: Resume text
            
        Returns:
            List of work history entries
        """
        work_history = []
        
        # Common date patterns
        date_patterns = [
            r'(\d{4})\s*[-–—]\s*(\d{4}|present|current)',
            r'(\d{1,2}/\d{4})\s*[-–—]\s*(\d{1,2}/\d{4}|present|current)',
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\s*[-–—]\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}|present|current',
        ]
        
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check if line contains date pattern
            for pattern in date_patterns:
                match = re.search(pattern, line.lower())
                if match:
                    # Extract job title (usually before or after dates)
                    job_title = re.sub(pattern, '', line, flags=re.IGNORECASE).strip()
                    
                    # Extract company (usually in next or previous line)
                    company = ''
                    if i + 1 < len(lines):
                        company = lines[i + 1].strip()
                    elif i > 0:
                        company = lines[i - 1].strip()
                    
                    # Calculate duration
                    start_year = match.group(1)
                    end_year = match.group(2) if match.group(2).lower() not in ['present', 'current'] else '2024'
                    
                    try:
                        start = int(re.search(r'\d{4}', start_year).group())
                        end = int(re.search(r'\d{4}', end_year).group())
                        duration = end - start
                    except:
                        duration = 0
                    
                    work_history.append({
                        'job_title': job_title[:100],  # Limit length
                        'company': company[:100],
                        'start_date': start_year,
                        'end_date': end_year,
                        'duration_years': duration,
                        'is_current': match.group(2).lower() in ['present', 'current']
                    })
                    break
        
        return work_history
    
    def calculate_total_experience(self, work_history: List[Dict]) -> float:
        """
        Calculate total years of experience from work history.
        
        Args:
            work_history: List of work history entries
            
        Returns:
            Total years of experience
        """
        if not work_history:
            return 0.0
        
        total_years = sum(entry.get('duration_years', 0) for entry in work_history)
        return float(total_years)
    
    def identify_career_progression(self, work_history: List[Dict]) -> Dict:
        """
        Analyze career progression from work history.
        
        Args:
            work_history: List of work history entries
            
        Returns:
            Career progression analysis
        """
        if not work_history:
            return {
                'progression': 'unknown',
                'message': 'No work history found',
                'trajectory': []
            }
        
        # Sort by start date
        sorted_history = sorted(
            work_history,
            key=lambda x: x.get('start_date', '0'),
            reverse=False
        )
        
        # Analyze job titles for seniority progression
        seniority_progression = []
        
        for entry in sorted_history:
            title = entry.get('job_title', '').lower()
            
            if any(term in title for term in ['junior', 'entry', 'intern', 'associate', 'assistant']):
                seniority_progression.append(1)  # Junior
            elif any(term in title for term in ['senior', 'sr.', 'lead', 'principal', 'staff']):
                seniority_progression.append(3)  # Senior
            elif any(term in title for term in ['manager', 'director', 'vp', 'head', 'chief']):
                seniority_progression.append(4)  # Leadership
            elif any(term in title for term in ['architect', 'expert', 'specialist']):
                seniority_progression.append(3)  # Expert
            else:
                seniority_progression.append(2)  # Mid-level
        
        # Determine progression pattern
        if len(seniority_progression) < 2:
            progression_type = 'single_role'
            message = 'Limited career history available'
        elif all(seniority_progression[i] <= seniority_progression[i+1] 
                 for i in range(len(seniority_progression)-1)):
            progression_type = 'upward'
            message = 'Consistent upward career progression'
        elif seniority_progression[-1] > seniority_progression[0]:
            progression_type = 'generally_upward'
            message = 'Overall positive career trajectory with some lateral moves'
        elif seniority_progression[-1] == seniority_progression[0]:
            progression_type = 'lateral'
            message = 'Lateral career moves at similar seniority levels'
        else:
            progression_type = 'mixed'
            message = 'Mixed career progression pattern'
        
        return {
            'progression': progression_type,
            'message': message,
            'trajectory': seniority_progression,
            'positions_count': len(sorted_history),
            'average_tenure': self.calculate_total_experience(sorted_history) / len(sorted_history) if sorted_history else 0
        }
    
    def score_experience_relevance(
        self,
        work_history: List[Dict],
        required_skills: List[str],
        job_title: str
    ) -> Dict:
        """
        Score how relevant the work experience is to the job.
        
        Args:
            work_history: List of work history entries
            required_skills: List of required skills
            job_title: Target job title
            
        Returns:
            Relevance scoring
        """
        if not work_history:
            return {
                'relevance_score': 0.0,
                'relevant_positions': 0,
                'total_positions': 0,
                'message': 'No work history found'
            }
        
        relevant_count = 0
        job_title_lower = job_title.lower()
        
        for entry in work_history:
            title = entry.get('job_title', '').lower()
            
            # Check if job title is similar
            title_match = any(
                word in title for word in job_title_lower.split()
                if len(word) > 3  # Skip short words like "the", "and"
            )
            
            # Check if required skills appear in role context
            # (This is simplified - in reality, would need full job description)
            if title_match:
                relevant_count += 1
        
        relevance_score = (relevant_count / len(work_history)) * 100 if work_history else 0
        
        return {
            'relevance_score': relevance_score,
            'relevant_positions': relevant_count,
            'total_positions': len(work_history),
            'message': f'{relevant_count} out of {len(work_history)} positions appear relevant'
        }


# Helper functions for standalone usage
def extract_experience_from_resume(resume_text: str) -> Dict:
    """
    Convenience function to extract all experience information from resume.
    
    Args:
        resume_text: Full resume text
        
    Returns:
        Dictionary with all experience information
    """
    scorer = ExperienceScorer()
    
    years = scorer.extract_years_from_text(resume_text)
    work_history = scorer.extract_work_history(resume_text)
    total_experience = scorer.calculate_total_experience(work_history)
    career_progression = scorer.identify_career_progression(work_history)
    
    return {
        'years_mentioned': years,
        'calculated_years': total_experience,
        'work_history': work_history,
        'career_progression': career_progression,
        'total_positions': len(work_history)
    }


def score_experience_match(
    resume_text: str,
    jd_text: str,
    job_title: str = "Unknown"
) -> Dict:
    """
    Convenience function to score experience match.
    
    Args:
        resume_text: Full resume text
        jd_text: Job description text
        job_title: Job title
        
    Returns:
        Complete experience scoring
    """
    scorer = ExperienceScorer()
    
    candidate_years = scorer.extract_years_from_text(resume_text)
    required_years = scorer.extract_years_from_text(jd_text)
    
    score = scorer.calculate_experience_score(candidate_years, required_years)
    gap_analysis = scorer.analyze_experience_gap(candidate_years, required_years)
    
    work_history = scorer.extract_work_history(resume_text)
    career_progression = scorer.identify_career_progression(work_history)
    
    return {
        'experience_score': score,
        'candidate_years': candidate_years,
        'required_years': required_years,
        'gap_analysis': gap_analysis,
        'work_history': work_history,
        'career_progression': career_progression
    }


if __name__ == "__main__":
    # Test the experience scorer
    print("Testing ExperienceScorer...")
    
    sample_resume = """
    John Doe
    Senior Software Engineer
    
    Experience:
    Senior Software Engineer | Tech Corp | 2020 - Present
    - Led development of microservices architecture
    
    Software Engineer | StartupXYZ | 2017 - 2020
    - Developed full-stack applications
    
    Junior Developer | WebCo | 2015 - 2017
    - Built responsive web applications
    
    Total: 8+ years of experience in software development
    """
    
    sample_jd = """
    We are looking for a Senior Software Engineer with 5+ years of experience
    in Python and cloud technologies.
    """
    
    scorer = ExperienceScorer()
    
    # Test extraction
    years = scorer.extract_years_from_text(sample_resume)
    print(f"\nExtracted years: {years}")
    
    # Test work history
    work_history = scorer.extract_work_history(sample_resume)
    print(f"\nWork history entries: {len(work_history)}")
    for entry in work_history:
        print(f"  - {entry['job_title']} ({entry['duration_years']} years)")
    
    # Test scoring
    required = scorer.extract_years_from_text(sample_jd)
    score = scorer.calculate_experience_score(years, required)
    print(f"\nExperience score: {score}/100")
    
    # Test gap analysis
    gap = scorer.analyze_experience_gap(years, required)
    print(f"\nGap analysis: {gap['status']}")
    print(f"Message: {gap['message']}")
    print(f"Recommendation: {gap['recommendation']}")
    
    # Test career progression
    progression = scorer.identify_career_progression(work_history)
    print(f"\nCareer progression: {progression['progression']}")
    print(f"Message: {progression['message']}")
    
    print("\n✅ All tests completed!")