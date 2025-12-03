"""
PDF text extraction with robust error handling.
"""
import os
from pathlib import Path


class PDFExtractor:
    """Extract text from PDF files using multiple methods."""
    
    def extract(self, filepath: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            filepath: Path to PDF file
            
        Returns:
            Extracted text string (never None)
            
        Raises:
            ValueError: If file doesn't exist or can't be read
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"PDF file not found: {filepath}")
        
        # Try pdfplumber first
        text = self._extract_with_pdfplumber(filepath)
        if text and len(text.strip()) > 50:
            return text
        
        # Fallback to PyPDF2
        text = self._extract_with_pypdf2(filepath)
        if text and len(text.strip()) > 50:
            return text
        
        # If both fail, raise clear error
        raise ValueError(
            f"Could not extract text from PDF: {filepath}\n"
            f"This PDF may be:\n"
            f"  • Scanned/image-based (requires OCR)\n"
            f"  • Corrupted or password-protected\n"
            f"  • Empty\n"
            f"Please convert to .txt or .docx format."
        )
    
    def _extract_with_pdfplumber(self, filepath: str) -> str:
        """Extract using pdfplumber library."""
        try:
            import pdfplumber
            
            text_parts = []
            with pdfplumber.open(filepath) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            
            return "\n\n".join(text_parts) if text_parts else ""
            
        except ImportError:
            return ""
        except Exception as e:
            print(f"⚠️ pdfplumber error: {e}")
            return ""
    
    def _extract_with_pypdf2(self, filepath: str) -> str:
        """Extract using PyPDF2 library."""
        try:
            import PyPDF2
            
            text_parts = []
            with open(filepath, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            
            return "\n\n".join(text_parts) if text_parts else ""
            
        except ImportError:
            return ""
        except Exception as e:
            print(f"⚠️ PyPDF2 error: {e}")
            return ""