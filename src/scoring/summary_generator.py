"""
Generate comprehensive analysis reports and summaries.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime


class SummaryGenerator:
    """Generate comprehensive analysis reports and summaries."""
    
    def __init__(self):
        """Initialize summary generator."""
        pass
    
    def generate_report(
        self,
        final_score: float,
        skill_score: float,
        semantic_score: float,
        experience_score: float,
        qualification_score: float,
        matched_skills_exact: List[str],
        matched_skills_fuzzy: List[str],
        matched_skills_semantic: List[str],
        missing_skills: List[str],
        extra_skills: List[str],
        semantic_similarity: float,
        experience_analysis: Dict[str, Any],
        resume_text: str,
        jd_text: str,
        job_title: Optional[str] = None,
        contact_info: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive analysis report.
        
        Args:
            final_score: Overall match score (0-100)
            skill_score: Skill matching score
            semantic_score: Semantic similarity score
            experience_score: Experience match score
            qualification_score: Qualification score
            matched_skills_exact: List of exact skill matches
            matched_skills_fuzzy: List of fuzzy skill matches
            matched_skills_semantic: List of semantic skill matches
            missing_skills: List of missing required skills
            extra_skills: List of extra skills (not required)
            semantic_similarity: Overall semantic similarity
            experience_analysis: Experience gap analysis
            resume_text: Full resume text
            jd_text: Full job description text
            job_title: Job title (optional)
            contact_info: Contact information (optional)
            
        Returns:
            Comprehensive report dictionary
        """
        # Calculate rating
        rating = self._calculate_rating(final_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            final_score,
            missing_skills,
            experience_analysis,
            matched_skills_exact,
            matched_skills_fuzzy
        )
        
        # Generate strengths
        strengths = self._identify_strengths(
            skill_score,
            semantic_score,
            experience_score,
            matched_skills_exact,
            matched_skills_fuzzy,
            extra_skills
        )
        
        # Build report
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'job_title': job_title or 'Not specified',
                'analyzer_version': '2.0.0'
            },
            'contact_info': contact_info or {},
            'overall_score': {
                'final_score': round(final_score, 1),
                'rating': rating,
                'breakdown': {
                    'skill_score': round(skill_score, 1),
                    'semantic_score': round(semantic_score, 1),
                    'experience_score': round(experience_score, 1),
                    'qualification_score': round(qualification_score, 1)
                }
            },
            'skills_analysis': {
                'matched_exact': matched_skills_exact,
                'matched_fuzzy': matched_skills_fuzzy,
                'matched_semantic': matched_skills_semantic,
                'missing': missing_skills,
                'extra': extra_skills,
                'total_matched': len(matched_skills_exact) + len(matched_skills_fuzzy) + len(matched_skills_semantic),
                'total_required': len(matched_skills_exact) + len(matched_skills_fuzzy) + len(matched_skills_semantic) + len(missing_skills),
                'match_rate': self._calculate_match_rate(
                    len(matched_skills_exact) + len(matched_skills_fuzzy) + len(matched_skills_semantic),
                    len(matched_skills_exact) + len(matched_skills_fuzzy) + len(matched_skills_semantic) + len(missing_skills)
                )
            },
            'semantic_analysis': {
                'overall_similarity': round(semantic_similarity, 3),
                'interpretation': self._interpret_semantic_score(semantic_similarity)
            },
            'experience_analysis': experience_analysis,
            'strengths': strengths,
            'recommendations': recommendations,
            'summary': self._generate_summary(
                final_score,
                rating,
                matched_skills_exact,
                matched_skills_fuzzy,
                missing_skills,
                experience_analysis
            )
        }
        
        return report
    
    def _calculate_rating(self, score: float) -> str:
        """Calculate rating based on score."""
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
    
    def _calculate_match_rate(self, matched: int, total: int) -> float:
        """Calculate match rate percentage."""
        if total == 0:
            return 0.0
        return round((matched / total) * 100, 1)
    
    def _interpret_semantic_score(self, score: float) -> str:
        """Interpret semantic similarity score."""
        if score >= 0.8:
            return "Very high semantic alignment with job requirements"
        elif score >= 0.7:
            return "High semantic alignment with job requirements"
        elif score >= 0.6:
            return "Moderate semantic alignment with job requirements"
        elif score >= 0.5:
            return "Fair semantic alignment with job requirements"
        else:
            return "Low semantic alignment with job requirements"
    
    def _generate_recommendations(
        self,
        final_score: float,
        missing_skills: List[str],
        experience_analysis: Dict[str, Any],
        matched_exact: List[str],
        matched_fuzzy: List[str]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Score-based recommendations
        if final_score < 70:
            recommendations.append(
                "Consider acquiring key missing skills through courses or projects"
            )
        
        # Missing skills recommendations
        if missing_skills:
            critical_missing = missing_skills[:5]
            if len(critical_missing) <= 3:
                recommendations.append(
                    f"Priority skills to acquire: {', '.join(critical_missing)}"
                )
            else:
                recommendations.append(
                    f"Focus on top missing skills: {', '.join(critical_missing[:3])}"
                )
        
        # Experience recommendations
        if experience_analysis and experience_analysis.get('status') in ['moderate_gap', 'significant_gap', 'critical_gap']:
            recommendations.append(experience_analysis.get('recommendation', ''))
        
        # Skill highlighting recommendations
        if matched_exact or matched_fuzzy:
            recommendations.append(
                "Highlight your relevant skills and projects more prominently in your resume"
            )
        
        # General recommendations based on score
        if final_score >= 80:
            recommendations.append(
                "Excellent match! Tailor your resume to emphasize relevant experience and projects"
            )
        elif final_score >= 70:
            recommendations.append(
                "Good match overall. Consider adding specific examples of projects using required skills"
            )
        elif final_score >= 60:
            recommendations.append(
                "Strengthen your profile by gaining hands-on experience with missing skills"
            )
        else:
            recommendations.append(
                "Significant skill gaps identified. Consider targeted learning or look for roles that better match your current skill set"
            )
        
        return recommendations
    
    def _identify_strengths(
        self,
        skill_score: float,
        semantic_score: float,
        experience_score: float,
        matched_exact: List[str],
        matched_fuzzy: List[str],
        extra_skills: List[str]
    ) -> List[str]:
        """Identify candidate's strengths."""
        strengths = []
        
        # Score-based strengths
        if skill_score >= 80:
            strengths.append(
                f"Strong skill match with {len(matched_exact)} exact and {len(matched_fuzzy)} similar skill matches"
            )
        
        if semantic_score >= 80:
            strengths.append(
                "High semantic alignment with job requirements"
            )
        
        if experience_score >= 90:
            strengths.append(
                "Experience level matches or exceeds requirements"
            )
        
        # Extra skills as strengths
        if extra_skills:
            notable_extra = [s for s in extra_skills if len(s) > 3][:5]
            if notable_extra:
                strengths.append(
                    f"Additional relevant skills: {', '.join(notable_extra[:3])}"
                )
        
        # Matched skills as strengths
        if matched_exact:
            key_matches = matched_exact[:5]
            strengths.append(
                f"Proficient in key required skills: {', '.join(key_matches[:3])}"
            )
        
        return strengths
    
    def _generate_summary(
        self,
        final_score: float,
        rating: str,
        matched_exact: List[str],
        matched_fuzzy: List[str],
        missing_skills: List[str],
        experience_analysis: Dict[str, Any]
    ) -> str:
        """Generate executive summary."""
        summary_parts = []
        
        # Overall assessment
        summary_parts.append(
            f"Overall Assessment: {rating} ({final_score:.1f}/100)"
        )
        
        # Skill summary
        total_matched = len(matched_exact) + len(matched_fuzzy)
        summary_parts.append(
            f"Skills: {total_matched} matched ({len(matched_exact)} exact, {len(matched_fuzzy)} similar), "
            f"{len(missing_skills)} missing"
        )
        
        # Experience summary
        if experience_analysis:
            exp_msg = experience_analysis.get('message', '')
            if exp_msg:
                summary_parts.append(f"Experience: {exp_msg}")
        
        # Key recommendation
        if final_score >= 80:
            summary_parts.append(
                "Recommendation: Strong candidate. Proceed with application."
            )
        elif final_score >= 70:
            summary_parts.append(
                "Recommendation: Good candidate. Consider applying with tailored resume."
            )
        elif final_score >= 60:
            summary_parts.append(
                "Recommendation: Fair match. Consider skill development before applying."
            )
        else:
            summary_parts.append(
                "Recommendation: Address significant skill gaps or consider alternative positions."
            )
        
        return " | ".join(summary_parts)
    
    def generate_detailed_analysis(
        self,
        report: Dict[str, Any]
    ) -> str:
        """
        Generate detailed text analysis from report.
        
        Args:
            report: Report dictionary from generate_report()
            
        Returns:
            Formatted text analysis
        """
        lines = []
        lines.append("=" * 80)
        lines.append("DETAILED RESUME ANALYSIS")
        lines.append("=" * 80)
        lines.append("")
        
        # Metadata
        metadata = report.get('metadata', {})
        lines.append(f"Analysis Date: {metadata.get('generated_at', 'N/A')}")
        lines.append(f"Job Title: {metadata.get('job_title', 'N/A')}")
        lines.append("")
        
        # Overall score
        overall = report.get('overall_score', {})
        lines.append(f"OVERALL SCORE: {overall.get('final_score', 0):.1f}/100")
        lines.append(f"Rating: {overall.get('rating', 'N/A')}")
        lines.append("")
        
        # Score breakdown
        breakdown = overall.get('breakdown', {})
        lines.append("Score Breakdown:")
        lines.append(f"  • Skill Match: {breakdown.get('skill_score', 0):.1f}/100")
        lines.append(f"  • Semantic Similarity: {breakdown.get('semantic_score', 0):.1f}/100")
        lines.append(f"  • Experience: {breakdown.get('experience_score', 0):.1f}/100")
        lines.append(f"  • Qualifications: {breakdown.get('qualification_score', 0):.1f}/100")
        lines.append("")
        
        # Skills analysis
        skills = report.get('skills_analysis', {})
        lines.append("SKILLS ANALYSIS:")
        lines.append(f"  Total Matched: {skills.get('total_matched', 0)}")
        lines.append(f"  Match Rate: {skills.get('match_rate', 0):.1f}%")
        lines.append("")
        
        # Matched skills
        if skills.get('matched_exact'):
            lines.append(f"  Exact Matches ({len(skills['matched_exact'])}):")
            for skill in skills['matched_exact'][:10]:
                lines.append(f"    ✓ {skill}")
            if len(skills['matched_exact']) > 10:
                lines.append(f"    ... and {len(skills['matched_exact']) - 10} more")
            lines.append("")
        
        # Missing skills
        if skills.get('missing'):
            lines.append(f"  Missing Skills ({len(skills['missing'])}):")
            for skill in skills['missing'][:10]:
                lines.append(f"    ✗ {skill}")
            if len(skills['missing']) > 10:
                lines.append(f"    ... and {len(skills['missing']) - 10} more")
            lines.append("")
        
        # Experience analysis
        exp = report.get('experience_analysis', {})
        if exp:
            lines.append("EXPERIENCE ANALYSIS:")
            lines.append(f"  {exp.get('message', 'N/A')}")
            lines.append(f"  Status: {exp.get('status', 'N/A')}")
            if exp.get('recommendation'):
                lines.append(f"  Recommendation: {exp['recommendation']}")
            lines.append("")
        
        # Strengths
        strengths = report.get('strengths', [])
        if strengths:
            lines.append("STRENGTHS:")
            for i, strength in enumerate(strengths, 1):
                lines.append(f"  {i}. {strength}")
            lines.append("")
        
        # Recommendations
        recommendations = report.get('recommendations', [])
        if recommendations:
            lines.append("RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"  {i}. {rec}")
            lines.append("")
        
        # Summary
        summary = report.get('summary', '')
        if summary:
            lines.append("SUMMARY:")
            lines.append(f"  {summary}")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def generate_json_report(self, report: Dict[str, Any]) -> str:
        """
        Generate JSON formatted report.
        
        Args:
            report: Report dictionary
            
        Returns:
            JSON string
        """
        import json
        return json.dumps(report, indent=2, ensure_ascii=False)