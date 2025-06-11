from typing import Dict, Any, List, Optional
import spacy
import scispacy
from transformers import AutoTokenizer, AutoModel
import torch
import logging
from src.config.model_config import NER_CONFIGS, TOOL_CONFIGS

logger = logging.getLogger(__name__)

class NERTool:
    """Tool for Named Entity Recognition using SciSpacy and BioBERT."""
    
    def __init__(self):
        self.config = TOOL_CONFIGS["ner"]
        self.scispacy_model = self._load_scispacy()
        self.biobert_model = self._load_biobert()
    
    def _load_scispacy(self) -> spacy.language.Language:
        """Load SciSpacy model.
        
        Returns:
            Loaded SciSpacy model
        """
        try:
            return spacy.load(NER_CONFIGS["scispacy"]["model"])
        except Exception as e:
            logger.error(f"Error loading SciSpacy model: {str(e)}")
            raise
    
    def _load_biobert(self) -> Dict[str, Any]:
        """Load BioBERT model and tokenizer.
        
        Returns:
            Dict containing model and tokenizer
        """
        try:
            model_name = NER_CONFIGS["biobert"]["model"]
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModel.from_pretrained(model_name)
            return {
                "model": model,
                "tokenizer": tokenizer
            }
        except Exception as e:
            logger.error(f"Error loading BioBERT model: {str(e)}")
            raise
    
    def extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract entities from text using both models.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict containing extracted entities
        """
        scispacy_entities = self._extract_scispacy_entities(text)
        biobert_entities = self._extract_biobert_entities(text)
        
        return {
            "scispacy": scispacy_entities,
            "biobert": biobert_entities,
            "combined": self._combine_entities(scispacy_entities, biobert_entities)
        }
    
    def _extract_scispacy_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using SciSpacy.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of extracted entities
        """
        doc = self.scispacy_model(text)
        entities = []
        
        for ent in doc.ents:
            if ent.label_ in ["DISEASE", "CHEMICAL", "GENE", "PROTEIN", "ORGANISM"]:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": 0.8  # Placeholder for confidence score
                })
        
        return entities
    
    def _extract_biobert_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using BioBERT.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of extracted entities
        """
        # Tokenize text
        inputs = self.biobert_model["tokenizer"](
            text,
            return_tensors="pt",
            max_length=self.config["max_length"],
            truncation=True,
            padding=True
        )
        
        # Get model outputs
        with torch.no_grad():
            outputs = self.biobert_model["model"](**inputs)
        
        # Process outputs (simplified version)
        # TODO: Implement proper entity extraction from BioBERT outputs
        return []
    
    def _combine_entities(
        self,
        scispacy_entities: List[Dict[str, Any]],
        biobert_entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Combine entities from both models.
        
        Args:
            scispacy_entities: Entities from SciSpacy
            biobert_entities: Entities from BioBERT
            
        Returns:
            Combined list of entities
        """
        # Create a set of unique entities based on text and label
        unique_entities = {}
        
        for entity in scispacy_entities + biobert_entities:
            key = (entity["text"], entity["label"])
            if key not in unique_entities:
                unique_entities[key] = entity
            else:
                # If entity exists, take the one with higher confidence
                if entity.get("confidence", 0) > unique_entities[key].get("confidence", 0):
                    unique_entities[key] = entity
        
        return list(unique_entities.values())
    
    def identify_therapeutic_areas(self, text: str) -> List[Dict[str, Any]]:
        """Identify therapeutic areas in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of identified therapeutic areas
        """
        entities = self.extract_entities(text)
        therapeutic_areas = []
        
        for entity in entities["combined"]:
            if entity["label"] == "DISEASE":
                therapeutic_areas.append({
                    "area": entity["text"],
                    "context": text[max(0, entity["start"] - 50):min(len(text), entity["end"] + 50)],
                    "confidence": entity.get("confidence", 0.8)
                })
        
        return therapeutic_areas
    
    def identify_moas(self, text: str) -> List[Dict[str, Any]]:
        """Identify mechanisms of action in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of identified mechanisms of action
        """
        entities = self.extract_entities(text)
        moas = []
        
        for entity in entities["combined"]:
            if entity["label"] in ["CHEMICAL", "PROTEIN", "GENE"]:
                moas.append({
                    "mechanism": entity["text"],
                    "context": text[max(0, entity["start"] - 50):min(len(text), entity["end"] + 50)],
                    "confidence": entity.get("confidence", 0.8)
                })
        
        return moas 