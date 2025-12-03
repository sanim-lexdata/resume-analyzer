import requests
import json
import os
from typing import List, Dict
from tqdm import tqdm

class ESCOFetcher:
    """
    Fetch and process ESCO (European Skills, Competences, Qualifications and Occupations) taxonomy.
    ESCO provides standardized skill descriptions used across Europe.
    """
    
    def __init__(self, cache_dir: str = "data/esco_cache"):
        self.cache_dir = cache_dir
        self.base_url = "https://ec.europa.eu/esco/api"
        os.makedirs(cache_dir, exist_ok=True)
        
        self.skills_cache_file = f"{cache_dir}/esco_skills.json"
        self.occupations_cache_file = f"{cache_dir}/esco_occupations.json"
    
    def fetch_skills(self, force_refresh: bool = False) -> Dict[str, List[Dict]]:
        """
        Fetch ESCO skills taxonomy.
        
        Args:
            force_refresh: Force re-download even if cached
            
        Returns:
            Dictionary of categorized skills
        """
        if os.path.exists(self.skills_cache_file) and not force_refresh:
            print("Loading ESCO skills from cache...")
            with open(self.skills_cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        print("Fetching ESCO skills from API...")
        
        # ESCO API endpoint for skills
        skills_url = f"{self.base_url}/resource/skill"
        
        all_skills = {
            'technical_skills': [],
            'transversal_skills': [],  # Soft skills
            'language_skills': [],
            'digital_skills': []
        }
        
        try:
            # Note: ESCO API requires proper authentication and pagination
            # This is a simplified example - you may need to adjust based on actual API
            
            # For demonstration, we'll use a predefined subset
            # In production, implement proper API calls with pagination
            
            predefined_skills = self._get_predefined_esco_skills()
            
            with open(self.skills_cache_file, 'w', encoding='utf-8') as f:
                json.dump(predefined_skills, f, indent=2, ensure_ascii=False)
            
            return predefined_skills
            
        except Exception as e:
            print(f"Error fetching ESCO skills: {e}")
            return self._get_predefined_esco_skills()
    
    def _get_predefined_esco_skills(self) -> Dict[str, List[Dict]]:
        """
        Get predefined ESCO skills for demonstration.
        In production, replace with actual API calls.
        """
        return {
            'technical_skills': [
                {'id': 'S1', 'name': 'Python programming', 'description': 'Programming in Python language'},
                {'id': 'S2', 'name': 'Java programming', 'description': 'Programming in Java language'},
                {'id': 'S3', 'name': 'JavaScript programming', 'description': 'Programming in JavaScript'},
                {'id': 'S4', 'name': 'SQL database management', 'description': 'Managing SQL databases'},
                {'id': 'S5', 'name': 'Cloud computing', 'description': 'Working with cloud platforms'},
                {'id': 'S6', 'name': 'Machine learning', 'description': 'Implementing ML algorithms'},
                {'id': 'S7', 'name': 'Data analysis', 'description': 'Analyzing data sets'},
                {'id': 'S8', 'name': 'Web development', 'description': 'Developing web applications'},
                {'id': 'S9', 'name': 'API development', 'description': 'Creating RESTful APIs'},
                {'id': 'S10', 'name': 'DevOps practices', 'description': 'Implementing DevOps methodologies'}
            ],
            'transversal_skills': [
                {'id': 'T1', 'name': 'Problem solving', 'description': 'Analytical problem solving'},
                {'id': 'T2', 'name': 'Team collaboration', 'description': 'Working effectively in teams'},
                {'id': 'T3', 'name': 'Communication', 'description': 'Effective communication skills'},
                {'id': 'T4', 'name': 'Leadership', 'description': 'Leading teams and projects'},
                {'id': 'T5', 'name': 'Time management', 'description': 'Managing time effectively'},
                {'id': 'T6', 'name': 'Critical thinking', 'description': 'Analytical and critical thinking'},
                {'id': 'T7', 'name': 'Adaptability', 'description': 'Adapting to change'},
                {'id': 'T8', 'name': 'Project management', 'description': 'Managing projects'}
            ],
            'language_skills': [
                {'id': 'L1', 'name': 'English', 'description': 'English language proficiency'},
                {'id': 'L2', 'name': 'Spanish', 'description': 'Spanish language proficiency'},
                {'id': 'L3', 'name': 'French', 'description': 'French language proficiency'},
                {'id': 'L4', 'name': 'German', 'description': 'German language proficiency'}
            ],
            'digital_skills': [
                {'id': 'D1', 'name': 'Digital literacy', 'description': 'Basic digital competence'},
                {'id': 'D2', 'name': 'Cybersecurity', 'description': 'Information security practices'},
                {'id': 'D3', 'name': 'Data privacy', 'description': 'Understanding data protection'},
                {'id': 'D4', 'name': 'Digital marketing', 'description': 'Online marketing skills'}
            ]
        }
    
    def search_skills(self, query: str, skills_data: Dict = None) -> List[Dict]:
        """
        Search for skills matching query.
        
        Args:
            query: Search query
            skills_data: Skills data to search in
            
        Returns:
            List of matching skills
        """
        if skills_data is None:
            skills_data = self.fetch_skills()
        
        query_lower = query.lower()
        matches = []
        
        for category, skills in skills_data.items():
            for skill in skills:
                if (query_lower in skill['name'].lower() or 
                    query_lower in skill['description'].lower()):
                    matches.append({**skill, 'category': category})
        
        return matches
    
    def get_all_skill_names(self) -> List[str]:
        """Get list of all skill names."""
        skills_data = self.fetch_skills()
        names = []
        
        for category, skills in skills_data.items():
            names.extend([skill['name'] for skill in skills])
        
        return names