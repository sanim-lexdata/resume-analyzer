import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForTokenClassification,
    pipeline
)
from typing import List, Dict, Set
import re

class HFSkillExtractor:
    """
    Extract skills using HuggingFace Transformers NER models.
    Uses BERT-based models fine-tuned for skill extraction.
    """
    
    def __init__(self, model_name: str = "jjzha/jobbert_skill_extraction"):
        """
        Initialize HuggingFace skill extractor.
        
        Args:
            model_name: HuggingFace model name
                Options:
                - "jjzha/jobbert_skill_extraction" (Job Description NER)
                - "dslim/bert-base-NER" (General NER)
                - "dbmdz/bert-large-cased-finetuned-conll03-english" (NER)
        """
        print(f"Loading HuggingFace model: {model_name}...")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForTokenClassification.from_pretrained(model_name)
            
            # Create NER pipeline
            self.ner_pipeline = pipeline(
                "ner",
                model=self.model,
                tokenizer=self.tokenizer,
                aggregation_strategy="simple"
            )
            
            self.model_name = model_name
            print(f"Model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            print("Falling back to general NER model...")
            
            # Fallback to general NER model
            self.model_name = "dslim/bert-base-NER"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForTokenClassification.from_pretrained(self.model_name)
            
            self.ner_pipeline = pipeline(
                "ner",
                model=self.model,
                tokenizer=self.tokenizer,
                aggregation_strategy="simple"
            )
    
    def extract_skills(self, text: str, confidence_threshold: float = 0.7) -> List[Dict]:
        """
        Extract skills from text using NER.
        
        Args:
            text: Input text (resume or job description)
            confidence_threshold: Minimum confidence score
            
        Returns:
            List of extracted skills with metadata
        """
        # Split text into chunks (transformers have token limits)
        chunks = self._split_text(text, max_length=512)
        
        all_entities = []
        
        for chunk in chunks:
            try:
                entities = self.ner_pipeline(chunk)
                
                for entity in entities:
                    if entity['score'] >= confidence_threshold:
                        all_entities.append({
                            'text': entity['word'],
                            'label': entity['entity_group'],
                            'score': entity['score'],
                            'start': entity.get('start', 0),
                            'end': entity.get('end', 0)
                        })
            except Exception as e:
                print(f"Error processing chunk: {e}")
                continue
        
        # Remove duplicates and filter
        unique_entities = self._deduplicate_entities(all_entities)
        
        return unique_entities
    
    def extract_technical_skills(self, text: str) -> List[str]:
        """
        Extract technical skills specifically.
        
        Args:
            text: Input text
            
        Returns:
            List of technical skill names
        """
        entities = self.extract_skills(text)
        
        technical_skills = []
        technical_labels = ['SKILL', 'TECH', 'ORG', 'PRODUCT']
        
        for entity in entities:
            if entity['label'] in technical_labels:
                technical_skills.append(entity['text'])
        
        return list(set(technical_skills))
    
    def extract_with_context(self, text: str, window_size: int = 50) -> List[Dict]:
        """
        Extract skills with surrounding context.
        
        Args:
            text: Input text
            window_size: Characters of context to include
            
        Returns:
            List of skills with context
        """
        entities = self.extract_skills(text)
        
        skills_with_context = []
        
        for entity in entities:
            start = entity['start']
            end = entity['end']
            
            context_start = max(0, start - window_size)
            context_end = min(len(text), end + window_size)
            
            context = text[context_start:context_end].strip()
            
            skills_with_context.append({
                'skill': entity['text'],
                'label': entity['label'],
                'score': entity['score'],
                'context': context
            })
        
        return skills_with_context
    
    def _split_text(self, text: str, max_length: int = 512) -> List[str]:
        """
        Split text into chunks for processing.
        
        Args:
            text: Input text
            max_length: Maximum chunk length in tokens
            
        Returns:
            List of text chunks
        """
        # Simple sentence-based splitting
        sentences = re.split(r'[.!?\n]+', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Rough estimate: 1 token ≈ 4 characters
            sentence_length = len(sentence) // 4
            
            if current_length + sentence_length > max_length:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _deduplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """
        Remove duplicate entities.
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            Deduplicated list
        """
        seen = set()
        unique = []
        
        for entity in entities:
            text_lower = entity['text'].lower().strip()
            
            if text_lower not in seen and len(text_lower) > 2:
                seen.add(text_lower)
                unique.append(entity)
        
        return unique
    
    def categorize_extracted_skills(self, entities: List[Dict], 
                                    skill_taxonomy: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Categorize extracted entities using a skill taxonomy.
        
        Args:
            entities: Extracted entities from NER
            skill_taxonomy: Dictionary of skill categories
            
        Returns:
            Categorized skills
        """
        categorized = {}
        uncategorized = []
        
        # Flatten taxonomy for lookup
        taxonomy_map = {}
        for category, skills in skill_taxonomy.items():
            for skill in skills:
                taxonomy_map[skill.lower()] = category
        
        for entity in entities:
            skill_name = entity['text']
            skill_lower = skill_name.lower()
            
            # Find matching category
            matched = False
            for known_skill, category in taxonomy_map.items():
                if known_skill in skill_lower or skill_lower in known_skill:
                    if category not in categorized:
                        categorized[category] = []
                    categorized[category].append(skill_name)
                    matched = True
                    break
            
            if not matched:
                uncategorized.append(skill_name)
        
        if uncategorized:
            categorized['uncategorized'] = uncategorized
        
        return categorized
    
    def batch_extract(self, texts: List[str]) -> List[List[Dict]]:
        """
        Extract skills from multiple texts.
        
        Args:
            texts: List of text documents
            
        Returns:
            List of skill extractions for each document
        """
        results = []
        
        for text in texts:
            skills = self.extract_skills(text)
            results.append(skills)
        
        return results