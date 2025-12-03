import re
from typing import List, Dict, Set
from collections import defaultdict

class JDSkillExtractor:
    """Extract required skills from job description."""
    
    def __init__(self, skills_dict: Dict[str, List[str]]):
        self.skills_dict = skills_dict
        self.all_skills = self._flatten_skills()
    
    def _flatten_skills(self) -> Set[str]:
        """Flatten all skills from dictionary."""
        all_skills = set()
        for category, skills in self.skills_dict.items():
            all_skills.update([skill.lower() for skill in skills])
        return all_skills
    
    def extract(self, jd_text: str) -> Dict[str, any]:
        """
        Extract required and preferred skills from job description.
        
        Args:
            jd_text: Job description text
            
        Returns:
            Dictionary with required and preferred skills
        """
        jd_lower = jd_text.lower()
        
        required_section = self._extract_section(jd_text, ['required', 'must have', 'requirements'])
        preferred_section = self._extract_section(jd_text, ['preferred', 'nice to have', 'bonus'])
        
        required_skills = self._extract_skills_from_text(required_section or jd_lower)
        preferred_skills = self._extract_skills_from_text(preferred_section or "")
        
        experience_req = self._extract_experience_requirement(jd_lower)
        education_req = self._extract_education_requirement(jd_text)
        
        return {
            'required_skills': required_skills,
            'preferred_skills': preferred_skills,
            'experience_requirement': experience_req,
            'education_requirement': education_req,
            'total_required_skills': sum(len(skills) for skills in required_skills.values())
        }
    
    def _extract_skills_from_text(self, text: str) -> Dict[str, List[str]]:
        """Extract skills from text section."""
        if not text:
            return {}
        
        text_lower = text.lower()
        found_skills = defaultdict(list)
        
        for category, skills in self.skills_dict.items():
            for skill in skills:
                if self._skill_exists(skill.lower(), text_lower):
                    found_skills[category].append(skill)
        
        return dict(found_skills)
    
    def _skill_exists(self, skill: str, text: str) -> bool:
        """Check if skill exists with word boundary."""
        pattern = r'\b' + re.escape(skill) + r'\b'
        return bool(re.search(pattern, text, re.IGNORECASE))
    
    def _extract_section(self, text: str, keywords: List[str]) -> str:
        """Extract text section based on keywords."""
        text_lower = text.lower()
        
        for keyword in keywords:
            pattern = rf'{keyword}[:\s]+(.*?)(?=\n\n|\Z)'
            match = re.search(pattern, text_lower, re.DOTALL)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_experience_requirement(self, text: str) -> Dict[str, any]:
        """Extract experience requirements."""
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
            r'experience[:\s]*(\d+)\+?\s*years?',
            r'minimum\s*(\d+)\s*years?'
        ]
        
        years = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            years.extend([int(m) for m in matches])
        
        if years:
            return {
                'min_years': min(years),
                'max_years': max(years),
                'required': True
            }
        
        return {'min_years': 0, 'max_years': 0, 'required': False}
    
    def _extract_education_requirement(self, text: str) -> Dict[str, any]:
        """Extract education requirements."""
        education_levels = {
            'phd': r'\b(phd|ph\.d|doctorate|doctoral)\b',
            'masters': r'\b(masters?|m\.s|msc|m\.sc|graduate degree)\b',
            'bachelors': r'\b(bachelors?|b\.s|bsc|b\.sc|undergraduate degree)\b',
            'associate': r'\b(associate|a\.s|asc)\b'
        }
        
        text_lower = text.lower()
        found_levels = []
        
        for level, pattern in education_levels.items():
            if re.search(pattern, text_lower):
                found_levels.append(level)
        
        return {
            'required_levels': found_levels,
            'required': len(found_levels) > 0
        }
    
    def identify_key_technologies(self, jd_text: str) -> List[str]:
        """
        Identify most important technologies mentioned multiple times.
        
        Args:
            jd_text: Job description text
            
        Returns:
            List of key technologies sorted by frequency
        """
        jd_lower = jd_text.lower()
        skill_counts = defaultdict(int)
        
        for category, skills in self.skills_dict.items():
            if category in ['programming_languages', 'web_technologies', 'databases', 'cloud_platforms']:
                for skill in skills:
                    count = len(re.findall(r'\b' + re.escape(skill.lower()) + r'\b', jd_lower))
                    if count > 0:
                        skill_counts[skill] = count
        
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
        return [skill for skill, count in sorted_skills[:10]]