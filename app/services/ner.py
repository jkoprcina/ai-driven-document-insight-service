"""
Named Entity Recognition (NER) service for extracting entities from text and answers.
Uses spaCy for efficient entity extraction and classification.
"""
import spacy
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class EntityRecognizer:
    """Extract and classify named entities from text."""
    
    def __init__(self, model: str = "en_core_web_sm"):
        """
        Initialize NER model.
        
        Args:
            model: spaCy model name (default: en_core_web_sm)
        """
        try:
            self.nlp = spacy.load(model)
        except OSError:
            logger.warning(f"Model {model} not found. NER service will be unavailable. "
                          f"To fix: python -m spacy download {model}")
            self.nlp = None
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities from text, grouped by type.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with entity types as keys and lists of entities as values
        """
        try:
            doc = self.nlp(text)
            entities = {}
            
            for ent in doc.ents:
                ent_type = ent.label_
                if ent_type not in entities:
                    entities[ent_type] = []
                entities[ent_type].append(ent.text)
            
            return entities
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {}
    
    def highlight_entities(self, text: str, format_type: str = "dict") -> Dict:
        """
        Highlight entities in text with positions and labels.
        
        Args:
            text: Input text
            format_type: Output format ('dict', 'html', 'markdown')
            
        Returns:
            Highlighted text with entity information
        """
        if not self.nlp:
            logger.warning("NER model not loaded, cannot highlight entities")
            return {"text": text, "entities": [], "error": "NER model unavailable"}
        
        try:
            doc = self.nlp(text)
            
            if format_type == "dict":
                return {
                    "text": text,
                    "entities": [
                        {
                            "text": ent.text,
                            "label": ent.label_,
                            "start": ent.start_char,
                            "end": ent.end_char,
                            "label_description": spacy.explain(ent.label_)
                        }
                        for ent in doc.ents
                    ]
                }
            
            elif format_type == "html":
                highlighted = text
                # Sort by position (reverse to maintain indices)
                for ent in sorted(doc.ents, key=lambda e: e.start_char, reverse=True):
                    tag = ent.label_.lower().replace("_", "-")
                    replacement = f'<mark class="entity {tag}" title="{ent.label_}">{ent.text}</mark>'
                    highlighted = highlighted[:ent.start_char] + replacement + highlighted[ent.end_char:]
                return {"text": highlighted, "format": "html"}
            
            elif format_type == "markdown":
                highlighted = text
                # Sort by position (reverse to maintain indices)
                for ent in sorted(doc.ents, key=lambda e: e.start_char, reverse=True):
                    replacement = f'**{ent.text}** ({ent.label_})'
                    highlighted = highlighted[:ent.start_char] + replacement + highlighted[ent.end_char:]
                return {"text": highlighted, "format": "markdown"}
            
            return {"text": text, "format": format_type}
        
        except Exception as e:
            logger.error(f"Error highlighting entities: {e}")
            return {"text": text, "error": str(e)}
    
    def get_entity_labels(self) -> Dict[str, str]:
        """Get descriptions of all entity label types."""
        labels = {}
        for label in self.nlp.get_pipe("ner").labels:
            labels[label] = spacy.explain(label)
        return labels
