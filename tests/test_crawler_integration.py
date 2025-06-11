import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from src.agents.crawler import CrawlerAgent

def test_crawler_with_biotech_website():
    """Test crawler with a real biotech company website."""
    agent = CrawlerAgent()
    
    # Test with a real biotech company website
    test_url = "https://www.modernatx.com/pipeline"
    result = agent.process(test_url)
    
    # Basic validation
    assert "error" not in result
    assert "source_url" in result
    assert "pipeline_info" in result
    assert "deal_info" in result
    assert "raw_text" in result
    
    # Pipeline info validation
    pipeline_info = result["pipeline_info"]
    assert "phases" in pipeline_info
    assert isinstance(pipeline_info["phases"], dict)
    
    # Deal info validation
    deal_info = result["deal_info"]
    assert "partnerships" in deal_info
    assert "licenses" in deal_info
    assert "acquisitions" in deal_info
    
    # Print results for manual inspection
    print("\nCrawler Results:")
    print("=" * 50)
    print(f"Source URL: {result['source_url']}")
    print("\nPipeline Phases Found:")
    for phase, contexts in pipeline_info["phases"].items():
        print(f"\n{phase}:")
        for context in contexts:
            if isinstance(context, dict):
                print(f"- {context.get('context', '')[:200]}...")
            else:
                print(f"- {str(context)[:200]}...")
    
    print("\nDeal Information:")
    for deal_type in ["partnerships", "licenses", "acquisitions"]:
        if deal_info[deal_type]:
            print(f"\n{deal_type.title()}:")
            for deal in deal_info[deal_type]:
                print(f"- {deal[:200]}...")

def test_crawler_with_company_name():
    """Test crawler with a company name (should return error as not implemented)."""
    agent = CrawlerAgent()
    result = agent.process("Moderna")
    
    # Should return error as company name processing is not implemented
    assert "error" in result
    assert "not implemented" in result["error"].lower()

def test_crawler_with_invalid_url():
    """Test crawler with an invalid URL."""
    agent = CrawlerAgent()
    result = agent.process("not-a-valid-url")
    
    # Should return error for invalid URL
    assert "error" in result

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 