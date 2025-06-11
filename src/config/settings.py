from typing import Dict, List
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, REPORTS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Business-specific settings
THERAPEUTIC_AREAS: List[str] = [
    "Oncology",
    "Cardiovascular",
    "Neurology",
    "Immunology",
    "Rare Diseases",
    "Infectious Diseases",
    "Metabolic Disorders",
    "Respiratory",
    "Gastroenterology",
    "Dermatology"
]

DEAL_TYPES: List[str] = [
    "Licensing",
    "Merger & Acquisition",
    "Collaboration",
    "Joint Venture",
    "Strategic Alliance",
    "Research Partnership",
    "Development Partnership",
    "Commercial Partnership"
]

PHASE_KEYWORDS: Dict[str, List[str]] = {
    "Pre-clinical": ["pre-clinical", "preclinical", "IND-enabling"],
    "Phase I": ["phase 1", "phase i", "first-in-human"],
    "Phase II": ["phase 2", "phase ii", "proof-of-concept"],
    "Phase III": ["phase 3", "phase iii", "pivotal"],
    "Approved": ["approved", "marketing authorization", "regulatory approval"]
}

# GPT-4 settings
GPT_SETTINGS = {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000,
    "system_prompt": """You are an expert pharmaceutical business development analyst with deep knowledge of:
    - Therapeutic areas and market dynamics
    - Drug development pipelines and clinical trials
    - Competitive landscape and market positioning
    - Business development strategies and deal structures
    - Regulatory environment and approval processes"""
}

# Report template settings
REPORT_TEMPLATE = {
    "sections": [
        "Executive Summary",
        "Opportunity Overview",
        "Market Analysis",
        "Competitive Landscape",
        "Risk Assessment",
        "Strategic Recommendations"
    ],
    "max_pages": 1,
    "format": "json"
}

# Crawler settings
CRAWLER_SETTINGS = {
    "timeout": 30,
    "max_retries": 3,
    "user_agent": "MarketPulse/1.0 (Business Development Analysis Tool)",
    "allowed_domains": [
        "biospace.com",
        "fiercebiotech.com",
        "pharmatimes.com",
        "pharmafile.com",
        "endpts.com",
        "biopharmadive.com"
    ]
} 