import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import time
from src.agents.crawler import CrawlerAgent

def test_crawler_performance():
    """Test the performance of the Crawler agent under load."""
    crawler = CrawlerAgent()
    start_time = time.time()
    
    # Simulate 10 requests
    for _ in range(10):
        crawler.process("https://example.com")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Ensure the total time is reasonable (e.g., less than 10 seconds)
    assert total_time < 10, f"Crawler performance test failed: {total_time} seconds for 10 requests"
    
    # Print performance metrics
    print(f"\n=== Crawler Performance Test ===")
    print(f"Total time for 10 requests: {total_time:.2f} seconds")
    print(f"Average time per request: {total_time / 10:.2f} seconds")
    print("===============================\n") 