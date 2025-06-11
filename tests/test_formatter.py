import pytest
from pathlib import Path
import json
from src.tools.formatter import ReportFormatter

@pytest.fixture
def sample_report_data():
    return {
        "executive_summary": "This is a test executive summary.",
        "therapeutic_areas": [
            {"name": "Oncology", "confidence": 0.95},
            {"name": "Cardiology", "confidence": 0.85}
        ],
        "mechanisms_of_action": [
            {"name": "PD-1 inhibition", "confidence": 0.90},
            {"name": "Angiogenesis inhibition", "confidence": 0.88}
        ],
        "market_analysis": {
            "market_potential": "High potential in oncology market",
            "competitive_landscape": [
                {
                    "company": "Company A",
                    "product": "Product X",
                    "stage": "Phase III"
                },
                {
                    "company": "Company B",
                    "product": "Product Y",
                    "stage": "Phase II"
                }
            ]
        },
        "risk_assessment": {
            "key_risks": [
                {
                    "description": "High competition in target market",
                    "severity": "high"
                },
                {
                    "description": "Regulatory approval timeline",
                    "severity": "medium"
                }
            ]
        },
        "recommendations": {
            "next_steps": [
                "Conduct additional market research",
                "Develop regulatory strategy"
            ]
        },
        "metadata": {
            "report_id": "TEST-001",
            "version": "1.0"
        }
    }

@pytest.fixture
def formatter():
    return ReportFormatter()

def test_format_json(formatter, sample_report_data, tmp_path):
    output_path = tmp_path / "test_report.json"
    result = formatter.format_report(
        sample_report_data,
        output_format="json",
        output_path=str(output_path)
    )
    
    assert "report" in result
    assert "metadata" in result
    assert result["metadata"]["format"] == "json"
    
    # Verify file was created
    assert output_path.exists()
    with open(output_path) as f:
        saved_data = json.load(f)
        assert saved_data == result

def test_format_html(formatter, sample_report_data, tmp_path):
    output_path = tmp_path / "test_report.html"
    result = formatter.format_report(
        sample_report_data,
        output_format="html",
        output_path=str(output_path)
    )
    
    assert "content" in result
    assert "metadata" in result
    assert result["metadata"]["format"] == "html"
    
    # Verify file was created
    assert output_path.exists()
    with open(output_path) as f:
        content = f.read()
        assert "Market Analysis Report" in content
        assert sample_report_data["executive_summary"] in content

def test_format_pdf(formatter, sample_report_data, tmp_path):
    output_path = tmp_path / "test_report.pdf"
    result = formatter.format_report(
        sample_report_data,
        output_format="pdf",
        output_path=str(output_path)
    )
    
    assert "content" in result
    assert "metadata" in result
    assert result["metadata"]["format"] == "pdf"
    
    # Verify file was created
    assert output_path.exists()

def test_create_one_page_summary(formatter, sample_report_data):
    summary = formatter.create_one_page_summary(sample_report_data)
    
    assert "executive_summary" in summary
    assert "key_findings" in summary
    assert "recommendations" in summary
    assert "metadata" in summary
    
    # Verify key findings structure
    key_findings = summary["key_findings"]
    assert "therapeutic_areas" in key_findings
    assert "mechanisms_of_action" in key_findings
    assert "market_potential" in key_findings
    assert "key_risks" in key_findings

def test_invalid_output_format(formatter, sample_report_data):
    with pytest.raises(ValueError):
        formatter.format_report(
            sample_report_data,
            output_format="invalid_format"
        ) 