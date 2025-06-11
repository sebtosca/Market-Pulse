import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.agents.crawler import CrawlerAgent

def main():
    # Initialize the crawler
    crawler = CrawlerAgent()
    
    # Test URL (Moderna's pipeline page)
    test_url = "https://www.modernatx.com/pipeline"
    
    print(f"Crawling: {test_url}")
    print("=" * 50)
    
    # Process the URL
    result = crawler.process(test_url)
    
    # Print results
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    print("\nPipeline Information:")
    print("-" * 30)
    for phase, contexts in result["pipeline_info"]["phases"].items():
        print(f"\n{phase}:")
        for context in contexts:
            print(f"- {context[:200]}...")
    
    print("\nDeal Information:")
    print("-" * 30)
    for deal_type in ["partnerships", "licenses", "acquisitions"]:
        if result["deal_info"][deal_type]:
            print(f"\n{deal_type.title()}:")
            for deal in result["deal_info"][deal_type]:
                print(f"- {deal[:200]}...")

if __name__ == "__main__":
    main() 