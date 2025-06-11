import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from src.agents.crawler import CrawlerAgent
from src.agents.analyst import AnalystAgent
from src.agents.advisor import AdvisorAgent
from unittest.mock import patch

def test_crawler_agent():
    """Test the crawler agent with a sample URL."""
    crawler = CrawlerAgent()
    result = crawler.process("https://example.com")
    
    assert isinstance(result, dict)
    assert "pipeline_info" in result
    assert "deal_info" in result
    assert "raw_text" in result

def test_analyst_agent():
    """Test the analyst agent with sample data."""
    analyst = AnalystAgent()
    sample_data = {
        "pipeline_info": {
            "phases": {
                "Phase I": [
                    {
                        "product": "Product A",
                        "context": "Small molecule inhibitor in Phase I for cancer treatment"
                    }
                ]
            }
        },
        "deal_info": {
            "partnerships": [
                {
                    "company": "Company X",
                    "context": "Strategic partnership for cancer drug development"
                }
            ],
            "licenses": [],
            "acquisitions": []
        }
    }
    
    result = analyst.process(sample_data)
    
    assert isinstance(result, dict)
    assert "therapeutic_areas" in result
    assert "mechanisms_of_action" in result
    assert "competitors" in result
    
    # Verify therapeutic areas
    assert len(result["therapeutic_areas"]) > 0
    assert any(area["area"] == "Oncology" for area in result["therapeutic_areas"])
    
    # Verify MOAs
    assert len(result["mechanisms_of_action"]) > 0
    assert any(moa["category"] == "Small Molecule" for moa in result["mechanisms_of_action"])
    
    # Verify competitors
    assert len(result["competitors"]) > 0
    assert any(comp["company"] == "Company X" for comp in result["competitors"])

def test_advisor_agent():
    """Test the advisor agent with sample analysis data."""
    advisor = AdvisorAgent()
    sample_analysis = {
        "therapeutic_areas": [
            {
                "area": "Oncology",
                "confidence": 0.8,
                "matches": [{"term": "cancer", "context": "cancer treatment"}]
            }
        ],
        "mechanisms_of_action": [
            {
                "category": "Small Molecule",
                "confidence": 0.8,
                "matches": [{"term": "inhibitor", "context": "small molecule inhibitor"}]
            }
        ],
        "competitors": [
            {
                "company": "Company X",
                "deal_type": "partnerships",
                "context": "Strategic partnership for cancer drug development"
            }
        ]
    }
    
    result = advisor.process(sample_analysis)
    
    assert isinstance(result, dict)
    assert "executive_summary" in result
    assert "opportunity_highlights" in result
    assert "key_risks" in result
    assert "strategic_recommendations" in result
    
    # Verify executive summary content
    assert "Oncology" in result["executive_summary"]
    assert "Small Molecule" in result["executive_summary"]
    assert "Company X" in result["executive_summary"]
    
    # Verify opportunity highlights
    assert "Oncology" in result["opportunity_highlights"]
    assert "Small Molecule" in result["opportunity_highlights"]
    
    # Verify key risks
    assert len(result["key_risks"]) > 0
    
    # Verify strategic recommendations
    assert len(result["strategic_recommendations"]) > 0

def test_full_pipeline():
    """Test the full pipeline from Crawler → Analyst → Advisor."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.text = """
        <html>
            <body>
                <h1>FOR IMMEDIATE RELEASE</h1>
                <p>Company Announces Phase 2 Clinical Trial Results</p>
                <p>About the Company</p>
            </body>
        </html>
        """
        # Step 1: Initialize agents
        crawler = CrawlerAgent()
        analyst = AnalystAgent()
        advisor = AdvisorAgent()
        
        # Step 2: Crawl a real press release (using a mock URL for testing)
        url = "https://example.com/press-release"
        raw_data = crawler.process(url)
        assert "pipeline_info" in raw_data or "deal_info" in raw_data, "Crawler failed to extract data"
        
        # Step 3: Analyze the crawled data
        analysis = analyst.process(raw_data)
        assert "therapeutic_areas" in analysis, "Analyst failed to identify therapeutic areas"
        assert "mechanisms_of_action" in analysis, "Analyst failed to identify MOAs"
        assert "competitors" in analysis, "Analyst failed to identify competitors"
        
        # Step 4: Generate the opportunity analysis report
        report = advisor.process(analysis)
        assert "executive_summary" in report, "Advisor failed to generate executive summary"
        assert "opportunity_highlights" in report, "Advisor failed to generate opportunity highlights"
        assert "key_risks" in report, "Advisor failed to generate key risks"
        assert "strategic_recommendations" in report, "Advisor failed to generate recommendations"
        
        # Step 5: Verify the report is coherent and actionable
        assert len(report["executive_summary"]) > 0, "Executive summary is empty"
        assert len(report["opportunity_highlights"]) > 0, "Opportunity highlights are empty"
        assert len(report["key_risks"]) > 0, "Key risks are empty"
        assert len(report["strategic_recommendations"]) > 0, "Strategic recommendations are empty"
        
        # Step 6: Print the report for manual inspection
        print("\n=== Full Pipeline Test Report ===")
        print(f"Executive Summary: {report['executive_summary']}")
        print(f"Opportunity Highlights: {report['opportunity_highlights']}")
        print(f"Key Risks: {report['key_risks']}")
        print(f"Strategic Recommendations: {report['strategic_recommendations']}")
        print("===============================\n") 