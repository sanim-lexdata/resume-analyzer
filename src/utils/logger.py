import logging
import os
import sys
from datetime import datetime

class Logger:
    """Custom logger for the resume analyzer application."""
    
    def __init__(self, name="ResumeAnalyzer", log_dir="output/logs"):
        self.name = name
        self.log_dir = log_dir
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with file and console handlers."""
        os.makedirs(self.log_dir, exist_ok=True)
        
        log_filename = f"{self.log_dir}/app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        if not self.logger.handlers:
            # File handler with UTF-8 encoding
            file_handler = logging.FileHandler(log_filename, encoding='utf-8', errors='replace')
            file_handler.setLevel(logging.DEBUG)
            
            # Console handler with UTF-8 encoding
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            # Try to set console to UTF-8 (for Windows)
            if hasattr(sys.stdout, 'reconfigure'):
                try:
                    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                except Exception:
                    pass
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def _clean_message(self, message):
        """Remove emoji and special characters that cause encoding issues on Windows."""
        # Remove common emoji characters
        emoji_chars = ['✅', '❌', '⚠️', '📊', '🔍', '💡', '📝', '✔️', '✖️']
        cleaned = str(message)
        for emoji in emoji_chars:
            cleaned = cleaned.replace(emoji, '')
        return cleaned.strip()
    
    def debug(self, message):
        self.logger.debug(self._clean_message(message))
    
    def info(self, message):
        self.logger.info(self._clean_message(message))
    
    def warning(self, message):
        self.logger.warning(self._clean_message(message))
    
    def error(self, message):
        self.logger.error(self._clean_message(message))
    
    def critical(self, message):
        self.logger.critical(self._clean_message(message))