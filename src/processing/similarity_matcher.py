"""
Skill similarity matching with fuzzy matching support.
"""
from fuzzywuzzy import fuzz
from typing import List, Dict, Set


class SimilarityMatcher:
    """Match skills using exact and fuzzy matching."""
    
    def __init__(self, default_threshold: int = 85):
        """
        Initialize similarity matcher.
        
        Args:
            default_threshold: Default fuzzy matching threshold (0-100)
        """
        self.default_threshold = default_threshold
    
    def match_skills(
        self, 
        resume_skills: List[str], 
        required_skills: List[str],
        threshold: int = None
    ) -> Dict[str, any]:
        """
        Match resume skills against required skills.
        
        Args:
            resume_skills: List of skills from resume
            required_skills: List of required skills from job description
            threshold: Fuzzy matching threshold (0-100), uses default if None
            
        Returns:
            Dictionary with matching results
        """
        if threshold is None:
            threshold = self.default_threshold
        
        # Normalize skills (lowercase, strip whitespace)
        resume_skills_normalized = [s.lower().strip() for s in resume_skills if s]
        required_skills_normalized = [s.lower().strip() for s in required_skills if s]
        
        # Convert to sets for exact matching
        resume_set = set(resume_skills_normalized)
        required_set = set(required_skills_normalized)
        
        # Exact matches
        matched_exact = list(resume_set & required_set)
        
        # Find fuzzy matches for unmatched required skills
        unmatched_required = required_set - set(matched_exact)
        unmatched_resume = resume_set - set(matched_exact)
        
        matched_fuzzy = []
        fuzzy_pairs = []
        
        for req_skill in unmatched_required:
            best_match = None
            best_score = 0
            
            for res_skill in unmatched_resume:
                score = fuzz.ratio(req_skill, res_skill)
                
                if score >= threshold and score > best_score:
                    best_score = score
                    best_match = res_skill
            
            if best_match:
                matched_fuzzy.append(req_skill)
                fuzzy_pairs.append({
                    'required': req_skill,
                    'resume': best_match,
                    'score': best_score
                })
                unmatched_resume.discard(best_match)
        
        # Missing skills (required but not found)
        missing = list(unmatched_required - set(matched_fuzzy))
        
        # Extra skills (in resume but not required)
        extra = list(unmatched_resume)
        
        return {
            'matched_exact': matched_exact,
            'matched_fuzzy': matched_fuzzy,
            'fuzzy_pairs': fuzzy_pairs,
            'missing': missing,
            'extra': extra,
            'total_required': len(required_skills_normalized),
            'total_matched': len(matched_exact) + len(matched_fuzzy),
            'match_percentage': (len(matched_exact) + len(matched_fuzzy)) / len(required_skills_normalized) * 100 if required_skills_normalized else 0
        }
    
    def calculate_skill_similarity(self, skill1: str, skill2: str) -> float:
        """
        Calculate similarity score between two skills.
        
        Args:
            skill1: First skill
            skill2: Second skill
            
        Returns:
            Similarity score (0-100)
        """
        return fuzz.ratio(skill1.lower().strip(), skill2.lower().strip())
    
    def find_similar_skills(
        self, 
        target_skill: str, 
        skill_list: List[str], 
        threshold: int = None,
        top_n: int = 5
    ) -> List[Dict[str, any]]:
        """
        Find similar skills from a list.
        
        Args:
            target_skill: Skill to match
            skill_list: List of skills to search
            threshold: Minimum similarity threshold
            top_n: Number of top matches to return
            
        Returns:
            List of matching skills with scores
        """
        if threshold is None:
            threshold = self.default_threshold
        
        matches = []
        target_normalized = target_skill.lower().strip()
        
        for skill in skill_list:
            skill_normalized = skill.lower().strip()
            score = fuzz.ratio(target_normalized, skill_normalized)
            
            if score >= threshold:
                matches.append({
                    'skill': skill,
                    'score': score
                })
        
        # Sort by score descending
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches[:top_n]
    
    def get_match_statistics(self, match_result: Dict) -> Dict[str, any]:
        """
        Calculate detailed matching statistics.
        
        Args:
            match_result: Result from match_skills()
            
        Returns:
            Dictionary with statistics
        """
        total_required = match_result['total_required']
        total_matched = match_result['total_matched']
        
        return {
            'total_required_skills': total_required,
            'total_matched_skills': total_matched,
            'exact_matches': len(match_result['matched_exact']),
            'fuzzy_matches': len(match_result['matched_fuzzy']),
            'missing_skills': len(match_result['missing']),
            'extra_skills': len(match_result['extra']),
            'match_rate': match_result['match_percentage'],
            'coverage': 'Excellent' if match_result['match_percentage'] >= 80 else
                       'Good' if match_result['match_percentage'] >= 60 else
                       'Fair' if match_result['match_percentage'] >= 40 else
                       'Poor'
        }
    
    def match_with_categories(
        self,
        resume_skills: Dict[str, List[str]],
        required_skills: Dict[str, List[str]],
        threshold: int = None
    ) -> Dict[str, Dict]:
        """
        Match skills organized by categories.
        
        Args:
            resume_skills: Dictionary of skill categories and lists
            required_skills: Dictionary of required skill categories and lists
            threshold: Fuzzy matching threshold
            
        Returns:
            Dictionary with matching results per category
        """
        if threshold is None:
            threshold = self.default_threshold
        
        results = {}
        
        for category, req_skills in required_skills.items():
            res_skills = resume_skills.get(category, [])
            
            results[category] = self.match_skills(
                res_skills,
                req_skills,
                threshold=threshold
            )
        
        return results
    
    def identify_skill_gaps(
        self,
        resume_skills: List[str],
        required_skills: List[str],
        threshold: int = None
    ) -> Dict[str, any]:
        """
        Identify critical skill gaps.
        
        Args:
            resume_skills: Skills from resume
            required_skills: Required skills
            threshold: Matching threshold
            
        Returns:
            Dictionary with gap analysis
        """
        match_result = self.match_skills(resume_skills, required_skills, threshold)
        
        missing_skills = match_result['missing']
        
        # Categorize by priority (basic heuristic)
        critical_gaps = []
        important_gaps = []
        nice_to_have = []
        
        for skill in missing_skills:
            skill_lower = skill.lower()
            
            # Critical: core technologies, required certifications
            if any(keyword in skill_lower for keyword in ['required', 'must', 'essential']):
                critical_gaps.append(skill)
            # Important: common technical skills
            elif any(keyword in skill_lower for keyword in ['python', 'java', 'sql', 'aws', 'docker']):
                important_gaps.append(skill)
            # Nice to have: everything else
            else:
                nice_to_have.append(skill)
        
        return {
            'critical_gaps': critical_gaps,
            'important_gaps': important_gaps,
            'nice_to_have': nice_to_have,
            'total_gaps': len(missing_skills),
            'gap_severity': 'High' if critical_gaps else 'Medium' if important_gaps else 'Low',
            'recommendations': self._generate_gap_recommendations(critical_gaps, important_gaps)
        }
    
    def _generate_gap_recommendations(
        self,
        critical_gaps: List[str],
        important_gaps: List[str]
    ) -> List[str]:
        """Generate recommendations based on skill gaps."""
        recommendations = []
        
        if critical_gaps:
            recommendations.append(
                f"Priority: Acquire critical skills: {', '.join(critical_gaps[:3])}"
            )
        
        if important_gaps:
            recommendations.append(
                f"Strengthen key technical skills: {', '.join(important_gaps[:3])}"
            )
        
        if not critical_gaps and not important_gaps:
            recommendations.append(
                "Good match! Consider highlighting relevant projects and experience."
            )
        
        return recommendations