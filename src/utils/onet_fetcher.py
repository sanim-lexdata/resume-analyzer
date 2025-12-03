import requests
import json
import os
from typing import List, Dict

class ONETFetcher:
    """
    Fetch and process O*NET (Occupational Information Network) data.
    O*NET is the US Department of Labor's occupational database.
    """
    
    def __init__(self, cache_dir: str = "data/onet_cache"):
        self.cache_dir = cache_dir
        # O*NET Web Services requires registration for API access
        # Visit: https://services.onetcenter.org/
        self.base_url = "https://services.onetcenter.org/ws"
        os.makedirs(cache_dir, exist_ok=True)
        
        self.skills_cache_file = f"{cache_dir}/onet_skills.json"
        self.occupations_cache_file = f"{cache_dir}/onet_occupations.json"
    
    def fetch_skills(self, force_refresh: bool = False) -> Dict[str, List[Dict]]:
        """
        Fetch O*NET skills taxonomy.
        
        Args:
            force_refresh: Force re-download even if cached
            
        Returns:
            Dictionary of categorized skills
        """
        if os.path.exists(self.skills_cache_file) and not force_refresh:
            print("Loading O*NET skills from cache...")
            with open(self.skills_cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        print("Loading O*NET skills...")
        
        # Using predefined O*NET skill taxonomy
        # In production, use actual O*NET API with credentials
        
        onet_skills = self._get_predefined_onet_skills()
        
        with open(self.skills_cache_file, 'w', encoding='utf-8') as f:
            json.dump(onet_skills, f, indent=2)
        
        return onet_skills
    
    def _get_predefined_onet_skills(self) -> Dict[str, List[Dict]]:
        """
        Get predefined O*NET skills taxonomy.
        Based on O*NET Content Model.
        """
        return {
            'basic_skills': [
                {'id': 'B1', 'name': 'Active Listening', 'description': 'Giving full attention to what other people are saying'},
                {'id': 'B2', 'name': 'Critical Thinking', 'description': 'Using logic and reasoning'},
                {'id': 'B3', 'name': 'Reading Comprehension', 'description': 'Understanding written sentences'},
                {'id': 'B4', 'name': 'Writing', 'description': 'Communicating effectively in writing'},
                {'id': 'B5', 'name': 'Speaking', 'description': 'Talking to others to convey information'},
                {'id': 'B6', 'name': 'Mathematics', 'description': 'Using mathematics to solve problems'},
                {'id': 'B7', 'name': 'Science', 'description': 'Using scientific rules and methods'}
            ],
            'cross_functional_skills': [
                {'id': 'C1', 'name': 'Complex Problem Solving', 'description': 'Identifying complex problems'},
                {'id': 'C2', 'name': 'Social Perceptiveness', 'description': 'Being aware of others reactions'},
                {'id': 'C3', 'name': 'Coordination', 'description': 'Adjusting actions in relation to others'},
                {'id': 'C4', 'name': 'Persuasion', 'description': 'Persuading others to change minds'},
                {'id': 'C5', 'name': 'Negotiation', 'description': 'Bringing others together'},
                {'id': 'C6', 'name': 'Instructing', 'description': 'Teaching others how to do something'},
                {'id': 'C7', 'name': 'Service Orientation', 'description': 'Actively looking for ways to help'}
            ],
            'technical_skills': [
                {'id': 'TS1', 'name': 'Programming', 'description': 'Writing computer programs'},
                {'id': 'TS2', 'name': 'Technology Design', 'description': 'Generating or adapting equipment'},
                {'id': 'TS3', 'name': 'Operations Analysis', 'description': 'Analyzing needs and product requirements'},
                {'id': 'TS4', 'name': 'Systems Analysis', 'description': 'Determining how a system should work'},
                {'id': 'TS5', 'name': 'Systems Evaluation', 'description': 'Identifying measures of system performance'},
                {'id': 'TS6', 'name': 'Equipment Selection', 'description': 'Determining tools and equipment needed'},
                {'id': 'TS7', 'name': 'Installation', 'description': 'Installing equipment and programs'},
                {'id': 'TS8', 'name': 'Testing', 'description': 'Conducting tests to determine effectiveness'},
                {'id': 'TS9', 'name': 'Troubleshooting', 'description': 'Determining causes of operating errors'},
                {'id': 'TS10', 'name': 'Quality Control', 'description': 'Testing quality or performance'}
            ],
            'resource_management_skills': [
                {'id': 'R1', 'name': 'Time Management', 'description': 'Managing one\'s own time'},
                {'id': 'R2', 'name': 'Management of Financial Resources', 'description': 'Determining budget expenditures'},
                {'id': 'R3', 'name': 'Management of Material Resources', 'description': 'Obtaining and seeing appropriate use of resources'},
                {'id': 'R4', 'name': 'Management of Personnel Resources', 'description': 'Motivating, developing, and directing people'}
            ],
            'system_skills': [
                {'id': 'SY1', 'name': 'Judgment and Decision Making', 'description': 'Considering costs and benefits'},
                {'id': 'SY2', 'name': 'Systems Analysis', 'description': 'Determining how a system should work'},
                {'id': 'SY3', 'name': 'Systems Evaluation', 'description': 'Identifying measures of system performance'}
            ]
        }
    
    def fetch_occupation_skills(self, occupation_code: str) -> List[Dict]:
        """
        Fetch skills for a specific O*NET occupation.
        
        Args:
            occupation_code: O*NET-SOC code (e.g., '15-1252.00' for Software Developers)
            
        Returns:
            List of skills for the occupation
        """
        # In production, use actual API call
        # For now, return sample data
        
        sample_occupations = {
            '15-1252.00': {  # Software Developers
                'title': 'Software Developers',
                'skills': [
                    'Programming', 'Critical Thinking', 'Complex Problem Solving',
                    'Active Learning', 'Systems Analysis', 'Technology Design'
                ]
            },
            '15-1244.00': {  # Network and Computer Systems Administrators
                'title': 'Network and Computer Systems Administrators',
                'skills': [
                    'Troubleshooting', 'Systems Analysis', 'Programming',
                    'Critical Thinking', 'Equipment Selection', 'Installation'
                ]
            }
        }
        
        return sample_occupations.get(occupation_code, {}).get('skills', [])
    
    def search_occupations(self, keyword: str) -> List[Dict]:
        """
        Search for occupations by keyword.
        
        Args:
            keyword: Search keyword
            
        Returns:
            List of matching occupations
        """
        # Sample occupation data
        occupations = [
            {
                'code': '15-1252.00',
                'title': 'Software Developers',
                'description': 'Research, design, and develop computer applications'
            },
            {
                'code': '15-1244.00',
                'title': 'Network and Computer Systems Administrators',
                'description': 'Install, configure, and maintain network systems'
            },
            {
                'code': '15-1299.08',
                'title': 'Web Developers',
                'description': 'Design and create websites'
            },
            {
                'code': '15-1211.00',
                'title': 'Computer Systems Analysts',
                'description': 'Analyze data processing problems'
            }
        ]
        
        keyword_lower = keyword.lower()
        matches = [
            occ for occ in occupations 
            if keyword_lower in occ['title'].lower() or 
               keyword_lower in occ['description'].lower()
        ]
        
        return matches
    
    def get_all_skill_names(self) -> List[str]:
        """Get list of all skill names."""
        skills_data = self.fetch_skills()
        names = []
        
        for category, skills in skills_data.items():
            names.extend([skill['name'] for skill in skills])
        
        return names
    
    def merge_with_custom_skills(self, custom_skills: Dict) -> Dict:
        """
        Merge O*NET skills with custom skill dictionary.
        
        Args:
            custom_skills: Custom skills dictionary
            
        Returns:
            Merged skills dictionary
        """
        onet_skills = self.fetch_skills()
        
        merged = {**custom_skills}
        
        for category, skills in onet_skills.items():
            if category not in merged:
                merged[category] = []
            
            skill_names = [skill['name'] for skill in skills]
            merged[category].extend(skill_names)
        
        # Remove duplicates
        for category in merged:
            merged[category] = list(set(merged[category]))
        
        return merged