from typing import Dict, Any, List, Optional
from datetime import datetime
import re
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """Validate if a string is a valid URL.
    
    Args:
        url: URL to validate
        
    Returns:
        bool indicating if URL is valid
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def validate_company_name(name: str) -> bool:
    """Validate if a string is a valid company name.
    
    Args:
        name: Company name to validate
        
    Returns:
        bool indicating if name is valid
    """
    if not name or len(name) < 2:
        return False
    
    # Check for common company name patterns
    patterns = [
        r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Pharma|Biotech|Therapeutics|Medical|Health|Life\s+Sciences)$',
        r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc\.|LLC|Ltd\.|Corp\.|Corporation)$'
    ]
    
    return any(re.match(pattern, name) for pattern in patterns)

def validate_pipeline_info(pipeline_info: Dict[str, Any]) -> bool:
    """Validate pipeline information structure.
    
    Args:
        pipeline_info: Pipeline information to validate
        
    Returns:
        bool indicating if pipeline info is valid
    """
    required_keys = {"products", "phases", "indications"}
    return all(key in pipeline_info for key in required_keys)

def validate_deal_info(deal_info: Dict[str, Any]) -> bool:
    """Validate deal information structure.
    
    Args:
        deal_info: Deal information to validate
        
    Returns:
        bool indicating if deal info is valid
    """
    required_keys = {"partnerships", "licenses", "acquisitions"}
    return all(key in deal_info for key in required_keys)

def validate_analysis(analysis: Dict[str, Any]) -> bool:
    """Validate analysis results structure.
    
    Args:
        analysis: Analysis results to validate
        
    Returns:
        bool indicating if analysis is valid
    """
    required_keys = {
        "therapeutic_areas",
        "mechanisms_of_action",
        "competitors",
        "market_analysis"
    }
    return all(key in analysis for key in required_keys)

def validate_report(report: Dict[str, Any]) -> bool:
    """Validate report structure.
    
    Args:
        report: Report to validate
        
    Returns:
        bool indicating if report is valid
    """
    required_keys = {
        "executive_summary",
        "opportunity_analysis",
        "risk_assessment",
        "recommendations",
        "generated_at"
    }
    
    if not all(key in report for key in required_keys):
        return False
    
    # Validate generated_at timestamp
    try:
        datetime.fromisoformat(report["generated_at"])
    except:
        return False
    
    return True

def validate_financial_terms(terms: List[Dict[str, Any]]) -> bool:
    """Validate financial terms structure.
    
    Args:
        terms: Financial terms to validate
        
    Returns:
        bool indicating if terms are valid
    """
    if not isinstance(terms, list):
        return False
    
    required_keys = {"type", "value", "context"}
    return all(
        isinstance(term, dict) and all(key in term for key in required_keys)
        for term in terms
    )

def validate_dates(dates: List[Dict[str, Any]]) -> bool:
    """Validate dates structure.
    
    Args:
        dates: Dates to validate
        
    Returns:
        bool indicating if dates are valid
    """
    if not isinstance(dates, list):
        return False
    
    required_keys = {"date", "context"}
    return all(
        isinstance(date, dict) and all(key in date for key in required_keys)
        for date in dates
    )

def validate_confidence_scores(scores: List[Dict[str, Any]]) -> bool:
    """Validate confidence scores structure.
    
    Args:
        scores: Confidence scores to validate
        
    Returns:
        bool indicating if scores are valid
    """
    if not isinstance(scores, list):
        return False
    
    return all(
        isinstance(score, dict) and
        "confidence" in score and
        isinstance(score["confidence"], (int, float)) and
        0 <= score["confidence"] <= 1
        for score in scores
    ) 