import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from src.agents.crawler import CrawlerAgent
import json

def test_crawler(input_data, input_type):
    """Test the crawler with either a URL or company name."""
    # Initialize the crawler
    crawler = CrawlerAgent()
    
    print(f"\nTesting crawler with {input_type}: {input_data}")
    print("=" * 50)
    
    # Process the input
    result = crawler.process(input_data)
    
    # Print results in a structured format
    print("\nResults:")
    print("-" * 30)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    # Print pipeline information
    print("\nPipeline Information:")
    print("-" * 20)
    for phase, drugs in result["pipeline_info"]["phases"].items():
        print(f"\n{phase}:")
        for drug in drugs:
            print(f"  Drug: {drug['drug_name']}")
            print(f"  Indication: {drug['indication']}")
            print(f"  Context: {drug['context'][:100]}...")
    
    # Print deal information
    print("\nDeal Information:")
    print("-" * 20)
    for deal_type, deals in result["deal_info"].items():
        if deals:
            print(f"\n{deal_type.title()}:")
            for deal in deals:
                print(f"  Partner: {deal['partner']}")
                print(f"  Context: {deal['context'][:100]}...")
    
    # Print entities
    print("\nNamed Entities:")
    print("-" * 20)
    for entity_type, entities in result["entities"].items():
        if entities:
            print(f"\n{entity_type}:")
            for entity in entities:
                print(f"  {entity}")
    
    return result

def main():
    # Test with a URL
    url = "https://www.modernatx.com/pipeline"
    test_crawler(url, "URL")
    
    # Test with a company name
    company_name = "Moderna"
    test_crawler(company_name, "company name")

if __name__ == "__main__":
    main() 