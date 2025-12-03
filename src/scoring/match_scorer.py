"""
Calculate match scores between resume and job description.
"""
from typing import Dict, Any


class MatchScorer:
    """Calculate various matching scores."""
    
    def __init__(self):
        """Initialize match scorer with default weights."""
        self.weights = {
            'skills': 0.4,
            'semantic': 0.3,
            'experience': 0.2,
            'qualifications': 0.1
        }
    
    def set_weights(self, weights: Dict[str, float]):
        """
        Set custom scoring weights.
        
        Args:
            weights: Dictionary with score weights (must sum to 1.0)
        """
        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        self.weights = weights
    
    def calculate_skill_match_score(
        self,
        matched_count: int,
        required_count: int,
        fuzzy_matched_count: int = 0
    ) -> float:
        """
        Calculate skill matching score.
        
        Args:
            matched_count: Number of exactly matched skills
            required_count: Total number of required skills
            fuzzy_matched_count: Number of fuzzy/semantic matched skills
            
        Returns:
            Score from 0-100
        """
        if required_count == 0:
            return 100.0
        
        # Calculate match rate
        total_matched = matched_count + (fuzzy_matched_count * 0.8)  # Fuzzy matches worth 80%
        match_rate = min(total_matched / required_count, 1.0)
        
        # Convert to 0-100 scale
        score = match_rate * 100
        
        return round(score, 1)
    
    def calculate_semantic_score(self, similarity: float) -> float:
        """
        Calculate semantic similarity score.
        
        Args:
            similarity: Cosine similarity (0-1)
            
        Returns:
            Score from 0-100
        """
        if not isinstance(similarity, (int, float)):
            return 0.0
        
        # Convert 0-1 similarity to 0-100 score
        score = max(0, min(similarity * 100, 100))
        
        return round(score, 1)
    
    def calculate_experience_score(
        self,
        candidate_years: float,
        required_years: float
    ) -> float:
        """
        Calculate experience match score.
        
        Args:
            candidate_years: Years of experience candidate has
            required_years: Years of experience required
            
        Returns:
            Score from 0-100
        """
        # Handle None or invalid values
        if candidate_years is None or required_years is None:
            return 50.0  # Neutral score when experience is unknown
        
        if required_years == 0:
            return 100.0
        
        # Calculate ratio
        ratio = candidate_years / required_years
        
        # Scoring logic
        if ratio >= 1.0:
            # Meets or exceeds requirements
            if ratio <= 1.5:
                score = 100.0
            elif ratio <= 2.0:
                score = 95.0  # Slightly overqualified
            else:
                score = 90.0  # Significantly overqualified
        elif ratio >= 0.8:
            # Close to requirements (80-99%)
            score = 85.0 + (ratio - 0.8) * 75  # 85-100 range
        elif ratio >= 0.6:
            # Moderate gap (60-79%)
            score = 70.0 + (ratio - 0.6) * 75  # 70-85 range
        elif ratio >= 0.4:
            # Significant gap (40-59%)
            score = 50.0 + (ratio - 0.4) * 100  # 50-70 range
        else:
            # Critical gap (<40%)
            score = ratio * 125  # 0-50 range
        
        return round(score, 1)
    
    def calculate_qualification_score(
        self,
        has_degree: bool = False,
        has_certifications: bool = False,
        years_experience: float = 0
    ) -> float:
        """
        Calculate qualification score.
        
        Args:
            has_degree: Whether candidate has required degree
            has_certifications: Whether candidate has relevant certifications
            years_experience: Years of experience
            
        Returns:
            Score from 0-100
        """
        score = 0.0
        
        # Degree contribution (40%)
        if has_degree:
            score += 40.0
        
        # Certification contribution (30%)
        if has_certifications:
            score += 30.0
        
        # Experience contribution (30%)
        if years_experience >= 5:
            score += 30.0
        elif years_experience >= 3:
            score += 20.0
        elif years_experience >= 1:
            score += 10.0
        
        return round(min(score, 100.0), 1)
    
    def calculate_final_score(
        self,
        skill_score: float,
        semantic_score: float,
        experience_score: float,
        qualification_score: float,
        weights: Dict[str, float] = None
    ) -> float:
        """
        Calculate weighted final score.
        
        Args:
            skill_score: Skill matching score (0-100)
            semantic_score: Semantic similarity score (0-100)
            experience_score: Experience match score (0-100)
            qualification_score: Qualification score (0-100)
            weights: Optional custom weights (uses default if None)
            
        Returns:
            Final weighted score (0-100)
        """
        # Use provided weights or defaults
        w = weights or self.weights
        
        # Ensure all scores are numbers
        skill_score = float(skill_score) if skill_score is not None else 0.0
        semantic_score = float(semantic_score) if semantic_score is not None else 0.0
        experience_score = float(experience_score) if experience_score is not None else 0.0
        qualification_score = float(qualification_score) if qualification_score is not None else 0.0
        
        # Calculate weighted average
        final_score = (
            skill_score * w.get('skills', 0.4) +
            semantic_score * w.get('semantic', 0.3) +
            experience_score * w.get('experience', 0.2) +
            qualification_score * w.get('qualifications', 0.1)
        )
        
        # Ensure score is in valid range
        final_score = max(0.0, min(final_score, 100.0))
        
        return round(final_score, 1)
    
    def get_rating(self, score: float) -> str:
        """
        Get rating description for a score.
        
        Args:
            score: Score (0-100)
            
        Returns:
            Rating description
        """
        if score >= 90:
            return "Excellent Match"
        elif score >= 80:
            return "Very Good Match"
        elif score >= 70:
            return "Good Match"
        elif score >= 60:
            return "Fair Match"
        elif score >= 50:
            return "Moderate Match"
        else:
            return "Weak Match"
    
    def calculate_comprehensive_score(
        self,
        resume_skills: list,
        required_skills: list,
        matched_exact: list,
        matched_fuzzy: list,
        semantic_similarity: float,
        candidate_experience: float,
        required_experience: float,
        has_degree: bool = False,
        has_certifications: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate all scores in one comprehensive analysis.
        
        Args:
            resume_skills: List of resume skills
            required_skills: List of required skills
            matched_exact: List of exact matches
            matched_fuzzy: List of fuzzy matches
            semantic_similarity: Semantic similarity (0-1)
            candidate_experience: Candidate's years of experience
            required_experience: Required years of experience
            has_degree: Whether candidate has degree
            has_certifications: Whether candidate has certifications
            
        Returns:
            Dictionary with all scores and analysis
        """
        # Calculate individual scores
        skill_score = self.calculate_skill_match_score(
            len(matched_exact),
            len(required_skills),
            len(matched_fuzzy)
        )
        
        semantic_score = self.calculate_semantic_score(semantic_similarity)
        
        experience_score = self.calculate_experience_score(
            candidate_experience,
            required_experience
        )
        
        qualification_score = self.calculate_qualification_score(
            has_degree,
            has_certifications,
            candidate_experience
        )
        
        # Calculate final score
        final_score = self.calculate_final_score(
            skill_score,
            semantic_score,
            experience_score,
            qualification_score
        )
        
        # Get rating
        rating = self.get_rating(final_score)
        
        return {
            'final_score': final_score,
            'rating': rating,
            'breakdown': {
                'skill_score': skill_score,
                'semantic_score': semantic_score,
                'experience_score': experience_score,
                'qualification_score': qualification_score
            },
            'weights': self.weights,
            'analysis': {
                'skills_matched': len(matched_exact) + len(matched_fuzzy),
                'skills_required': len(required_skills),
                'match_rate': round((len(matched_exact) + len(matched_fuzzy)) / len(required_skills) * 100, 1) if required_skills else 0
            }
        }
    
    def compare_scores(
        self,
        score1: Dict[str, Any],
        score2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare two score results.
        
        Args:
            score1: First score dictionary
            score2: Second score dictionary
            
        Returns:
            Comparison analysis
        """
        return {
            'score_difference': score1['final_score'] - score2['final_score'],
            'better_score': 'score1' if score1['final_score'] > score2['final_score'] else 'score2',
            'skill_difference': score1['breakdown']['skill_score'] - score2['breakdown']['skill_score'],
            'semantic_difference': score1['breakdown']['semantic_score'] - score2['breakdown']['semantic_score'],
            'experience_difference': score1['breakdown']['experience_score'] - score2['breakdown']['experience_score']
        }