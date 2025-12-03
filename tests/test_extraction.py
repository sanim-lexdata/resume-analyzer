import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from extraction.text_cleaner import TextCleaner

class TestTextCleaner:
    """Test text cleaning functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.cleaner = TextCleaner(lowercase=True, remove_stopwords=False)
    
    def test_remove_urls(self):
        """Test URL removal."""
        text = "Check my portfolio at https://example.com for more info"
        cleaned = self.cleaner.clean(text)
        assert "https://example.com" not in cleaned
        assert "portfolio" in cleaned
    
    def test_remove_emails(self):
        """Test email removal."""
        text = "Contact me at john.doe@example.com for details"
        cleaned = self.cleaner.clean(text)
        assert "john.doe@example.com" not in cleaned
        assert "contact" in cleaned
    
    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        text = "Python     Developer   with    experience"
        cleaned = self.cleaner.clean(text)
        assert "  " not in cleaned
    
    def test_lowercase_conversion(self):
        """Test lowercase conversion."""
        text = "Python JAVASCRIPT React"
        cleaned = self.cleaner.clean(text)
        assert cleaned == "python javascript react"
    
    def test_remove_special_chars(self):
        """Test special character removal."""
        text = "Skills: • Python • Java • C++"
        cleaned = self.cleaner.clean(text)
        assert "•" not in cleaned

class TestSkillExtraction:
    """Test skill extraction."""
    
    def test_basic_extraction(self):
        """Test basic skill extraction."""
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])