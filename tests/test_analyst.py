import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from src.agents.analyst import AnalystAgent

def test_analyst_initialization():
    """Test analyst agent initialization."""
    agent = AnalystAgent()
    assert agent.name == "AnalystAgent"
    assert "therapeutic_areas" in agent.__dict__
    assert "mechanisms_of_action" in agent.__dict__

def test_therapeutic_area_identification():
    """Test identification of therapeutic areas."""
    agent = AnalystAgent()
    text = """
    Our lead product is in Phase II clinical trials for cancer treatment.
    We also have a pre-clinical candidate for multiple sclerosis.
    Our IND-enabled program shows promising results in rheumatoid arthritis.
    """
    
    areas = agent._identify_therapeutic_areas(text)
    
    # Test oncology identification
    oncology = next((area for area in areas if area["area"] == "Oncology"), None)
    assert oncology is not None
    assert oncology["confidence"] > 0
    assert any("cancer" in match["term"] for match in oncology["matches"])
    
    # Test neurology identification
    neurology = next((area for area in areas if area["area"] == "Neurology"), None)
    assert neurology is not None
    assert neurology["confidence"] > 0
    assert any("multiple sclerosis" in match["term"] for match in neurology["matches"])
    
    # Test immunology identification
    immunology = next((area for area in areas if area["area"] == "Immunology"), None)
    assert immunology is not None
    assert immunology["confidence"] > 0
    assert any("rheumatoid arthritis" in match["term"] for match in immunology["matches"])

def test_moa_identification():
    """Test identification of mechanisms of action."""
    agent = AnalystAgent()
    text = """
    Our lead product is a small molecule inhibitor targeting cancer.
    We also have a monoclonal antibody in development.
    Our cell therapy program shows promising results.
    """
    
    moas = agent._identify_moas(text)
    
    # Test small molecule identification
    small_molecule = next((moa for moa in moas if moa["category"] == "Small Molecule"), None)
    assert small_molecule is not None
    assert small_molecule["confidence"] > 0
    assert any("small molecule" in match["term"] for match in small_molecule["matches"])
    
    # Test biologic identification
    biologic = next((moa for moa in moas if moa["category"] == "Biologic"), None)
    assert biologic is not None
    assert biologic["confidence"] > 0
    assert any("monoclonal" in match["term"] for match in biologic["matches"])
    
    # Test cell therapy identification
    cell_therapy = next((moa for moa in moas if moa["category"] == "Cell Therapy"), None)
    assert cell_therapy is not None
    assert cell_therapy["confidence"] > 0
    assert any("cell therapy" in match["term"] for match in cell_therapy["matches"])

def test_competitor_identification():
    """Test identification of competitors."""
    agent = AnalystAgent()
    data = {
        "deal_info": {
            "partnerships": [
                {"company": "Pfizer", "context": "Strategic partnership for cancer drug"},
                {"company": "Novartis", "context": "Collaboration for MS treatment"}
            ],
            "licenses": [
                {"company": "Roche", "context": "License agreement for antibody technology"}
            ],
            "acquisitions": []
        }
    }
    result = agent.process(data)
    competitors = result.get("competitors", [])
    assert any("Pfizer" in c.get("name", "") for c in competitors)
    assert any("Novartis" in c.get("name", "") for c in competitors)
    assert any("Roche" in c.get("name", "") for c in competitors)

def test_full_analysis():
    """Test full analysis of pipeline and deal information."""
    agent = AnalystAgent()
    data = {
        "pipeline_info": {
            "phases": {
                "Phase II": [
                    {
                        "product": "XYZ-123",
                        "context": "Small molecule inhibitor in Phase II for cancer treatment by Pfizer"
                    }
                ],
                "Pre-clinical": [
                    {
                        "product": "ABC-456",
                        "context": "Monoclonal antibody in pre-clinical development for MS by Novartis"
                    }
                ]
            }
        },
        "deal_info": {
            "partnerships": [
                {
                    "company": "Pfizer",
                    "context": "Strategic partnership for cancer drug development"
                }
            ],
            "licenses": [],
            "acquisitions": []
        }
    }
    analysis = agent.process(data)
    # Test therapeutic areas
    assert len(analysis["therapeutic_areas"]) > 0
    assert any(area["area"] == "Oncology" for area in analysis["therapeutic_areas"])
    assert any(area["area"] == "Neurology" for area in analysis["therapeutic_areas"])
    # Test MOAs
    assert len(analysis["mechanisms_of_action"]) > 0
    assert any(moa["category"] == "Small Molecule" for moa in analysis["mechanisms_of_action"])
    assert any(moa["category"] == "Biologic" for moa in analysis["mechanisms_of_action"])
    # Test competitors
    competitors = analysis.get("competitors", [])
    assert any("Pfizer" in c.get("name", "") for c in competitors)
    assert any("Novartis" in c.get("name", "") for c in competitors)

def test_competitor_detection():
    """Test competitor detection with therapeutic area context."""
    agent = AnalystAgent()

    # Test data with real company names in therapeutic contexts
    test_data = {
        "pipeline_info": {
            "phases": {
                "Phase 1": [{
                    "context": "Pfizer is developing a novel cancer treatment targeting EGFR"
                }],
                "Phase 2": [{
                    "context": "Novartis has a similar approach in oncology"
                }]
            }
        },
        "deal_info": {
            "partnerships": [{
                "context": "Strategic alliance with Roche for neurological disorders"
            }]
        }
    }

    result = agent.process(test_data)

    assert "competitors" in result
    competitors = result["competitors"]
    assert len(competitors) > 0

    # Verify competitor detection
    competitor_names = [c["name"] for c in competitors]
    assert "Pfizer" in competitor_names
    assert "Novartis" in competitor_names
    assert "Roche" in competitor_names

def test_deal_structure_detection():
    """Test detection of different deal structures."""
    agent = AnalystAgent()
    
    # Test data with various deal types
    test_data = {
        "deal_info": {
            "partnerships": [{
                "context": "Announced co-development agreement with Partner X"
            }],
            "licenses": [{
                "context": "Exclusive licensing deal for novel technology"
            }],
            "acquisitions": [{
                "context": "Completed acquisition of Target Company"
            }]
        }
    }
    
    result = agent.process(test_data)
    
    assert "deals" in result
    deals = result["deals"]
    assert len(deals) > 0
    
    # Verify deal types
    deal_types = [d["type"] for d in deals]
    assert "co_development" in deal_types
    assert "licensing" in deal_types
    assert "acquisition" in deal_types
    
    # Verify context extraction
    for deal in deals:
        assert "context" in deal
        assert len(deal["context"]) > 0

def test_competitor_name_cleaning():
    """Test competitor name cleaning and deduplication."""
    agent = AnalystAgent()
    
    # Test data with various company name formats
    test_data = {
        "deal_info": {
            "partnerships": [
                {"company": "MerckEarly Inc.", "context": "Strategic partnership"},
                {"company": "PfizerBioNTech", "context": "Vaccine development"},
                {"company": "JohnsonJohnson", "context": "Drug development"},
                {"company": "The Novartis Corporation", "context": "Research collaboration"},
                {"company": "Roche Ltd.", "context": "Clinical trial"}
            ],
            "licenses": [
                {"company": "AstraZeneca PLC", "context": "License agreement"},
                {"company": "MerckEarly", "context": "Technology license"}  # Duplicate
            ],
            "acquisitions": [
                {"company": "Bristol Myers Squibb Co.", "context": "Acquisition"}
            ]
        }
    }
    
    result = agent.process(test_data)
    
    # Verify competitors were cleaned and deduplicated
    assert "competitors" in result
    competitors = result["competitors"]
    
    # Check number of unique competitors
    assert len(competitors) == 7  # Should be 7 unique companies
    
    # Check specific company names were cleaned correctly
    company_names = [c["name"] for c in competitors]
    assert "Merck" in company_names
    assert "Pfizer" in company_names
    assert "Johnson & Johnson" in company_names
    assert "Novartis" in company_names
    assert "Roche" in company_names
    assert "AstraZeneca" in company_names
    assert "Bristol Myers Squibb" in company_names
    
    # Verify no duplicates
    assert len(company_names) == len(set(company_names))
    
    # Verify confidence scores
    for comp in competitors:
        assert "confidence" in comp
        assert 0 <= comp["confidence"] <= 1 