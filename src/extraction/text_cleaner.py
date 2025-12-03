import re
from typing import List, Optional

class TextCleaner:
    """Clean and normalize extracted text."""
    
    def __init__(self, remove_stopwords: bool = False, lowercase: bool = True):
        self.remove_stopwords = remove_stopwords
        self.lowercase = lowercase
        
        self.stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
    
    def clean(self, text: str) -> str:
        """
        Clean text with multiple processing steps.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        text = self._remove_urls(text)
        text = self._remove_emails(text)
        text = self._normalize_whitespace(text)
        text = self._remove_special_chars(text)
        text = self._normalize_bullets(text)
        
        if self.lowercase:
            text = text.lower()
        
        if self.remove_stopwords:
            text = self._remove_stopwords_from_text(text)
        
        return text.strip()
    
    def _remove_urls(self, text: str) -> str:
        """Remove URLs from text."""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.sub(url_pattern, '', text)
    
    def _remove_emails(self, text: str) -> str:
        """Remove email addresses from text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.sub(email_pattern, '', text)
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace and line breaks."""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        return text
    
    def _remove_special_chars(self, text: str) -> str:
        """Remove or normalize special characters."""
        text = re.sub(r'[•●○■□▪▫]', '', text)
        text = re.sub(r'[^\w\s\n\.\,\-\+\#\(\)]', ' ', text)
        return text
    
    def _normalize_bullets(self, text: str) -> str:
        """Normalize bullet points and list markers."""
        text = re.sub(r'^[\s]*[-•●○■□▪▫]\s*', '', text, flags=re.MULTILINE)
        return text
    
    def _remove_stopwords_from_text(self, text: str) -> str:
        """Remove stopwords from text."""
        words = text.split()
        filtered_words = [word for word in words if word.lower() not in self.stopwords]
        return ' '.join(filtered_words)
    
    def extract_sections(self, text: str) -> dict:
        """
        Attempt to extract common resume sections.
        
        Args:
            text: Cleaned resume text
            
        Returns:
            Dictionary with identified sections
        """
        sections = {
            'education': [],
            'experience': [],
            'skills': [],
            'certifications': [],
            'projects': []
        }
        
        patterns = {
            'education': r'(?i)(education|academic|qualification)',
            'experience': r'(?i)(experience|employment|work history)',
            'skills': r'(?i)(skills|technical skills|competencies)',
            'certifications': r'(?i)(certification|certificate|license)',
            'projects': r'(?i)(projects|portfolio)'
        }
        
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            for section, pattern in patterns.items():
                if re.search(pattern, line):
                    current_section = section
                    break
            
            if current_section and line:
                sections[current_section].append(line)
        
        return sections