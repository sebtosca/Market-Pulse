from typing import List, Dict, Any
import re
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from src.config.settings import THERAPEUTIC_AREAS, DEAL_TYPES, PHASE_KEYWORDS

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def clean_text(text: str) -> str:
    """Clean and normalize text content.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep important ones
    text = re.sub(r'[^\w\s.,;:!?()-]', ' ', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text.strip()

def extract_sentences(text: str, max_length: int = 200) -> List[str]:
    """Extract meaningful sentences from text.
    
    Args:
        text: Text to process
        max_length: Maximum sentence length
        
    Returns:
        List of extracted sentences
    """
    sentences = sent_tokenize(text)
    return [s for s in sentences if len(s) <= max_length]

def identify_therapeutic_areas(text: str) -> List[Dict[str, Any]]:
    """Identify therapeutic areas mentioned in text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of identified therapeutic areas with context
    """
    areas = []
    for area in THERAPEUTIC_AREAS:
        pattern = re.compile(rf'\b{re.escape(area)}\b', re.IGNORECASE)
        matches = pattern.finditer(text)
        for match in matches:
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end]
            areas.append({
                "area": area,
                "context": context,
                "confidence": 0.8  # Placeholder for ML-based confidence
            })
    return areas

def identify_deal_types(text: str) -> List[Dict[str, Any]]:
    """Identify deal types mentioned in text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of identified deal types with context
    """
    deals = []
    for deal_type in DEAL_TYPES:
        pattern = re.compile(rf'\b{re.escape(deal_type)}\b', re.IGNORECASE)
        matches = pattern.finditer(text)
        for match in matches:
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end]
            deals.append({
                "type": deal_type,
                "context": context,
                "confidence": 0.8  # Placeholder for ML-based confidence
            })
    return deals

def identify_development_phases(text: str) -> List[Dict[str, Any]]:
    """Identify development phases mentioned in text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of identified phases with context
    """
    phases = []
    for phase, keywords in PHASE_KEYWORDS.items():
        for keyword in keywords:
            pattern = re.compile(rf'\b{re.escape(keyword)}\b', re.IGNORECASE)
            matches = pattern.finditer(text)
            for match in matches:
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]
                phases.append({
                    "phase": phase,
                    "keyword": keyword,
                    "context": context,
                    "confidence": 0.8  # Placeholder for ML-based confidence
                })
    return phases

def extract_company_names(text: str) -> List[str]:
    """Extract company names from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of company names
    """
    # Common company name patterns
    patterns = [
        r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Pharma|Biotech|Therapeutics|Medical|Health|Life\s+Sciences)\b',
        r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc\.|LLC|Ltd\.|Corp\.|Corporation)\b'
    ]
    
    companies = set()
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        companies.update(match.group() for match in matches)
    
    return list(companies)

def extract_financial_terms(text: str) -> List[Dict[str, Any]]:
    """Extract financial terms and amounts from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of financial terms with context
    """
    # Common financial term patterns
    patterns = {
        "amount": r'\$?\d+(?:,\d{3})*(?:\.\d+)?\s*(?:million|billion|trillion)?',
        "percentage": r'\d+(?:\.\d+)?%',
        "currency": r'\$?\d+(?:,\d{3})*(?:\.\d+)?\s*(?:USD|EUR|GBP)'
    }
    
    terms = []
    for term_type, pattern in patterns.items():
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end]
            terms.append({
                "type": term_type,
                "value": match.group(),
                "context": context
            })
    
    return terms

def extract_dates(text: str) -> List[Dict[str, Any]]:
    """Extract dates from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of dates with context
    """
    # Common date patterns
    patterns = [
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
        r'\b\d{4}-\d{2}-\d{2}\b'
    ]
    
    dates = []
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end]
            dates.append({
                "date": match.group(),
                "context": context
            })
    
    return dates 