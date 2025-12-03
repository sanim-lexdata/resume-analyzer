import re
import spacy
from typing import List, Dict, Set
from collections import defaultdict

class SkillExtractor:
    """Extract skills from resume text."""
    
    def __init__(self, skills_dict: Dict[str, List[str]], spacy_model: str = "en_core_web_md"):
        self.skills_dict = skills_dict
        self.all_skills = self._flatten_skills()
        
        try:
            self.nlp = spacy.load(spacy_model)
        except OSError:
            print(f"Downloading spaCy model: {spacy_model}")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", spacy_model])
            self.nlp = spacy.load(spacy_model)
    
    def _flatten_skills(self) -> Set[str]:
        """Flatten all skills from dictionary into a set."""
        all_skills = set()
        for category, skills in self.skills_dict.items():
            all_skills.update([skill.lower() for skill in skills])
        return all_skills
    
    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Extract skills from text using multiple methods.
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary of categorized skills
        """
        text_lower = text.lower()
        found_skills = defaultdict(list)
        
        for category, skills in self.skills_dict.items():
            for skill in skills:
                if self._skill_exists(skill.lower(), text_lower):
                    found_skills[category].append(skill)
        
        found_skills = dict(found_skills)
        
        ner_skills = self._extract_with_ner(text)
        if ner_skills:
            if 'extracted_entities' not in found_skills:
                found_skills['extracted_entities'] = []
            found_skills['extracted_entities'].extend(ner_skills)
        
        return found_skills
    
    def _skill_exists(self, skill: str, text: str) -> bool:
        """
        Check if skill exists in text with word boundary matching.
        
        Args:
            skill: Skill to search for
            text: Text to search in
            
        Returns:
            True if skill found
        """
        pattern = r'\b' + re.escape(skill) + r'\b'
        return bool(re.search(pattern, text, re.IGNORECASE))
    
    def _extract_with_ner(self, text: str) -> List[str]:
        """
        Extract potential skills using spaCy NER.
        
        Args:
            text: Resume text
            
        Returns:
            List of extracted entities
        """
        doc = self.nlp(text[:100000])
        
        entities = []
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'GPE', 'NORP']:
                if len(ent.text) > 2 and ent.text.lower() not in self.all_skills:
                    entities.append(ent.text)
        
        return list(set(entities))[:20]
    
    def extract_years_of_experience(self, text: str) -> Dict[str, int]:
        """
        Extract years of experience mentioned in text.
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary with experience information
        """
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
            r'experience[:\s]*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s*(?:of)?\s*experience'
        ]
        
        years = []
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            years.extend([int(m) for m in matches])
        
        if years:
            return {
                'max_years': max(years),
                'total_mentions': len(years)
            }
        
        return {'max_years': 0, 'total_mentions': 0}
    
    def get_skill_count(self, extracted_skills: Dict[str, List[str]]) -> int:
        """
        Count total unique skills extracted.
        
        Args:
            extracted_skills: Dictionary of categorized skills
            
        Returns:
            Total count of unique skills
        """
        all_skills = []
        for category, skills in extracted_skills.items():
            if category != 'extracted_entities':
                all_skills.extend(skills)
        return len(set(all_skills))
    
    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Categorize a list of skills.
        
        Args:
            skills: List of skill names
            
        Returns:
            Dictionary of categorized skills
        """
        categorized = defaultdict(list)
        
        for skill in skills:
            skill_lower = skill.lower()
            found_category = None
            
            for category, category_skills in self.skills_dict.items():
                if skill_lower in [s.lower() for s in category_skills]:
                    found_category = category
                    break
            
            if found_category:
                categorized[found_category].append(skill)
            else:
                categorized['other'].append(skill)
        
        return dict(categorized)
    