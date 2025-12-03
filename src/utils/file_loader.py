import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any

class FileLoader:
    """Utility class for loading configuration and data files."""
    
    @staticmethod
    def load_yaml(filepath: str) -> Dict[str, Any]:
        """Load YAML configuration file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"YAML file not found: {filepath}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file: {e}")
    
    @staticmethod
    def load_json(filepath: str) -> Dict[str, Any]:
        """Load JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {filepath}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON file: {e}")
    
    @staticmethod
    def save_json(data: Dict[str, Any], filepath: str) -> None:
        """Save data as JSON file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def read_text_file(filepath: str) -> str:
        """Read plain text file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Text file not found: {filepath}")
        except Exception as e:
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception:
                raise ValueError(f"Error reading text file: {e}")
    
    @staticmethod
    def detect_file_type(filepath: str) -> str:
        """Detect file type from extension."""
        ext = Path(filepath).suffix.lower()
        type_mapping = {
            '.pdf': 'pdf',
            '.docx': 'docx',
            '.doc': 'doc',
            '.txt': 'txt',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml'
        }
        return type_mapping.get(ext, 'unknown')
    
    @staticmethod
    def ensure_directory(directory: str) -> None:
        """Ensure directory exists, create if not."""
        os.makedirs(directory, exist_ok=True)