import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from src.agents.crawler import CrawlerAgent
import json
from typing import Dict, Any

def print_results(result: Dict[str, Any], title: str = "Results"):
    """Print results in a formatted way."""
    print(f"\n=== Results for {title} ===")
    print("=" * 50)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    # Print URL
    if "url" in result:
        print(f"\nURL: {result['url']}")
    
    # Print Pipeline Information
    if "pipeline_info" in result:
        print("\nPipeline Information:")
        print("-" * 30)
        for phase, drugs in result["pipeline_info"].items():
            print(f"\n{phase}:")
            for drug in drugs:
                print(f"  Drug: {drug['drug']}")
                print(f"  Indication: {drug['indication']}")
                print(f"  Context: {drug['context']}")
    
    # Print Deal Information
    if "deal_info" in result:
        print("\nDeal Information:")
        print("-" * 30)
        for deal_type, deals in result["deal_info"].items():
            print(f"\n{deal_type.title()}:")
            for deal in deals:
                print(f"  Partner: {deal['partner']}")
                print(f"  Context: {deal['context']}")
    
    # Print Named Entities
    if "entities" in result:
        print("\nNamed Entities:")
        print("-" * 30)
        for entity_type, entities in result["entities"].items():
            print(f"\n{entity_type}:")
            for entity in entities:
                print(f"  {entity}")

def test_company_crawler():
    """Test the crawler with different company names."""
    crawler = CrawlerAgent()
    
    # Test companies
    test_companies = [
        "Moderna",
        "Pfizer",
        "Johnson & Johnson",
        "Novartis"
    ]
    
    for company in test_companies:
        print(f"\nTesting company: {company}")
        print("=" * 50)
        
        result = crawler.process(company)
        print_results(result, f"Company: {company}")
        
        # Add a small delay between requests
        time.sleep(2)

def test_url_crawler():
    """Test the crawler with specific URLs."""
    crawler = CrawlerAgent()
    
    # Test URLs
    test_urls = [
        "https://www.modernatx.com/pipeline",
        "https://www.pfizer.com/science/therapeutic-areas",
        "https://www.jnj.com/innovation/pipeline",
        "https://www.novartis.com/research-development/pipeline"
    ]
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        print("=" * 50)
        
        result = crawler.process(url)
        print_results(result, f"URL: {url}")
        
        # Add a small delay between requests
        time.sleep(2)

def main():
    """Main function to run the tests."""
    print("Starting Enhanced Crawler Tests")
    print("=" * 50)
    
    # Test with company names
    print("\nTesting with Company Names")
    print("=" * 50)
    test_company_crawler()
    
    # Test with URLs
    print("\nTesting with URLs")
    print("=" * 50)
    test_url_crawler()

if __name__ == "__main__":
    main() 