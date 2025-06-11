import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from src.agents.crawler import CrawlerAgent

def test_crawler_initialization():
    """Test crawler agent initialization."""
    agent = CrawlerAgent()
    assert agent.name == "CrawlerAgent"
    assert "User-Agent" in agent.headers
    assert "pharma_terms" in agent.__dict__

def test_url_validation():
    """Test URL validation functionality."""
    agent = CrawlerAgent()
    
    # Valid URLs
    assert agent._is_url("https://www.example.com")
    assert agent._is_url("http://test.com/path")
    
    # Invalid URLs
    assert not agent._is_url("not a url")
    assert not agent._is_url("example.com")  # Missing protocol

def test_text_extraction():
    """Test text extraction from HTML."""
    agent = CrawlerAgent()
    html = """
    <html>
        <body>
            <h1>Test Title</h1>
            <p>Test paragraph</p>
            <script>var x = 1;</script>
            <style>.test { color: red; }</style>
        </body>
    </html>
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    text = agent._extract_text_content(soup)
    
    assert "Test Title" in text
    assert "Test paragraph" in text
    assert "var x = 1" not in text  # Script content should be removed
    assert ".test" not in text  # Style content should be removed

def test_text_preprocessing():
    """Test press release preprocessing functionality."""
    agent = CrawlerAgent()
    text = """
    FOR IMMEDIATE RELEASE
    
    Company Announces Phase 2 Clinical Trial Results
    
    BOSTON, MA - Company X today announced positive results from its Phase 2 clinical trial of drug Y for the treatment of disease Z.
    
    The trial met its primary endpoint with statistical significance.
    
    About the Company
    Company X is a leading biotech company focused on developing innovative therapies.
    
    Forward-Looking Statements
    This press release contains forward-looking statements...
    
    Media Contact:
    John Doe
    john.doe@company.com
    
    SOURCE: Company X
    © 2024 Company X. All rights reserved.
    """
    processed = agent.preprocess_press_release(text)
    
    # Test removal of common artifacts
    assert "FOR IMMEDIATE RELEASE" not in processed
    assert "Media Contact:" not in processed
    assert "SOURCE:" not in processed
    assert "All rights reserved" not in processed
    
    # Test removal of boilerplate sections
    assert "About the Company" not in processed
    assert "Forward-Looking Statements" not in processed
    
    # Test preservation of relevant content
    assert "Phase 2 clinical trial" in processed
    assert "positive results" in processed
    assert "primary endpoint" in processed
    
    # Test text truncation
    words = processed.split()
    assert len(words) <= 500
    
    # Test relevant section extraction
    assert "clinical trial" in processed.lower()
    assert "phase 2" in processed.lower()

def test_structured_data_extraction():
    """Test structured data extraction."""
    agent = CrawlerAgent()
    text = """
    Our lead product XYZ-123 is in Phase II clinical trials for cancer treatment.
    We also have ABC-456 in pre-clinical development for rare diseases.
    Our IND-enabled program DEF-789 shows promising results.
    We announced a strategic partnership with Company X.
    Our licensing agreement with Company Y was successful.
    The recent acquisition of Company Z strengthens our portfolio.
    """
    
    structured_data = agent._extract_structured_data(text)
    
    # Test phase extraction
    assert "Phase II" in structured_data["phases"]
    assert "Pre-clinical" in structured_data["phases"]
    assert "IND" in structured_data["phases"]
    
    # Test product name extraction
    phase_ii_data = structured_data["phases"]["Phase II"][0]
    assert "XYZ-123" in phase_ii_data["product"]
    assert "cancer" in phase_ii_data["context"].lower()
    
    # Test deal extraction
    assert "partnership" in structured_data["deals"]
    assert "license" in structured_data["deals"]
    assert "acquisition" in structured_data["deals"]
    
    # Test company name extraction
    partnership_data = structured_data["deals"]["partnership"][0]
    assert "Company X" in partnership_data["company"]
    assert "strategic" in partnership_data["context"].lower()

def test_pipeline_info_extraction():
    """Test pipeline information extraction."""
    agent = CrawlerAgent()
    text = """
    Our lead product is in Phase II clinical trials for cancer treatment.
    We also have a pre-clinical candidate for rare diseases.
    Our IND-enabled program shows promising results.
    """
    
    structured_data = agent._extract_structured_data(text)
    pipeline_info = {"phases": structured_data["phases"]}
    
    assert "Phase II" in pipeline_info["phases"]
    assert "Pre-clinical" in pipeline_info["phases"]
    assert "IND" in pipeline_info["phases"]
    assert len(pipeline_info["phases"]["Phase II"]) > 0

def test_deal_info_extraction():
    """Test deal information extraction."""
    agent = CrawlerAgent()
    text = """
    We announced a strategic partnership with Company X.
    Our licensing agreement with Company Y was successful.
    The recent acquisition of Company Z strengthens our portfolio.
    """
    
    structured_data = agent._extract_structured_data(text)
    deal_info = {
        "partnerships": structured_data["deals"].get("partnership", []),
        "licenses": structured_data["deals"].get("license", []),
        "acquisitions": structured_data["deals"].get("acquisition", [])
    }
    
    assert len(deal_info["partnerships"]) > 0
    assert len(deal_info["licenses"]) > 0
    assert len(deal_info["acquisitions"]) > 0
    assert "Company X" in deal_info["partnerships"][0]["company"]
    assert "Company Y" in deal_info["licenses"][0]["company"]
    assert "Company Z" in deal_info["acquisitions"][0]["company"]

def jaccard_similarity(a, b):
    set_a = set(a.lower().split())
    set_b = set(b.lower().split())
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)

def test_preprocessing_jaccard_score():
    agent = CrawlerAgent()
    raw = """
    FOR IMMEDIATE RELEASE
    Company Announces Phase 2 Clinical Trial Results
    About the Company
    """
    expected = "Company Announces Phase 2 Clinical Trial Results"
    processed = agent.preprocess_press_release(raw)
    score = jaccard_similarity(processed, expected)
    print(f"Jaccard similarity: {score:.2f}")
    assert score > 0.7  # You can adjust this threshold as needed 

def test_html_cleaning():
    """Test that HTML cleaning returns clean text with actual content."""
    agent = CrawlerAgent()
    raw_html = """
    <html>
        <body>
            <div>Skip to main content...</div>
            <p>This is the actual content.</p>
        </body>
    </html>
    """
    cleaned = agent.clean_html(raw_html)
    # Check that the actual content is present
    assert "This is the actual content" in cleaned
    # Check that the text is properly normalized (no extra spaces)
    assert cleaned == "This is the actual content." 