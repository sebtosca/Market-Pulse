import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from unittest.mock import patch
from src.agents.crawler import CrawlerAgent

def test_crawler_api_integration():
    """Test how the Crawler agent interacts with external APIs."""
    with patch('requests.get') as mock_get:
        # Mock a successful API response
        mock_get.return_value.text = """
        <html>
            <body>
                <h1>FOR IMMEDIATE RELEASE</h1>
                <p>Company Announces Phase 2 Clinical Trial Results</p>
                <p>About the Company</p>
            </body>
        </html>
        """
        crawler = CrawlerAgent()
        result = crawler.process("https://example.com")
        assert "pipeline_info" in result or "deal_info" in result, "Crawler failed to extract data from mock API response"

def test_crawler_api_error_handling():
    """Test how the Crawler agent handles API errors."""
    with patch('requests.get') as mock_get:
        # Mock an API error
        mock_get.side_effect = Exception("API Error")
        crawler = CrawlerAgent()
        result = crawler.process("https://example.com")
        assert "error" in result, "Crawler failed to handle API error"
        assert "API Error" in result["error"], "Crawler did not return the correct error message" 