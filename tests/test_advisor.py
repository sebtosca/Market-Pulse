import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from src.agents.advisor import AdvisorAgent

def test_advisor_initialization():
    agent = AdvisorAgent()
    assert agent.name == "AdvisorAgent"

def test_advisor_report_structure():
    agent = AdvisorAgent()
    analyst_output = {
        "therapeutic_areas": [
            {"area": "Oncology", "matches": [{"term": "cancer", "context": "..."}], "confidence": 0.5},
            {"area": "Neurology", "matches": [{"term": "multiple sclerosis", "context": "..."}], "confidence": 0.3}
        ],
        "mechanisms_of_action": [
            {"category": "Small Molecule", "matches": [{"term": "inhibitor", "context": "..."}], "confidence": 0.5},
            {"category": "Biologic", "matches": [{"term": "antibody", "context": "..."}], "confidence": 0.2}
        ],
        "competitors": [
            {"company": "Company X", "deal_type": "partnerships", "context": "..."},
            {"company": "Company Y", "deal_type": "licenses", "context": "..."}
        ]
    }
    report = agent.process(analyst_output)
    assert isinstance(report, dict)
    assert "executive_summary" in report
    assert "opportunity_highlights" in report
    assert "key_risks" in report
    assert "strategic_recommendations" in report
    assert "generated_at" in report
    # Check that the executive summary is a string and contains key info
    assert isinstance(report["executive_summary"], str)
    assert "Oncology" in report["executive_summary"]
    assert "Small Molecule" in report["executive_summary"]
    assert "Company X" in report["executive_summary"]

def test_advisor_empty_input():
    agent = AdvisorAgent()
    empty_output = {"therapeutic_areas": [], "mechanisms_of_action": [], "competitors": []}
    report = agent.process(empty_output)
    assert "Unclear therapeutic focus." in report["key_risks"]
    assert "No clear mechanism of action identified." in report["key_risks"]
    assert "No competitors or partners identified" in report["key_risks"]
    assert "Gather more data" in report["strategic_recommendations"]

def test_advisor_error_passthrough():
    agent = AdvisorAgent()
    error_input = {"error": "Some error occurred"}
    report = agent.process(error_input)
    assert report["error"] == "Some error occurred" 