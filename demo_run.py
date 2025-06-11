from src.agents.crawler import CrawlerAgent
from src.agents.analyst import AnalystAgent
from src.agents.advisor import AdvisorAgent

def main():
    # Initialize agents
    print("Initializing agents...")
    crawler = CrawlerAgent()
    analyst = AnalystAgent()
    advisor = AdvisorAgent()

    # Test input
    input_data = "https://www.biopharmadive.com/press-release/20250610-echosens-and-boehringer-ingelheim-expand-long-standing-collaboration-to-acc/"
    print(f"\nInput URL: {input_data}")

    try:
        # Step 1: Crawl
        print("\n=== Agent 1: Crawler ===")
        crawl_result = crawler.process(input_data)
        print("Crawled Data (truncated):", str(crawl_result)[:500], "...\n")
        
        if not crawl_result or "error" in crawl_result:
            print("Crawler failed:", crawl_result)
            return

        # Step 2: Analyze
        print("=== Agent 2: Analyst ===")
        analysis_result = analyst.process(crawl_result)
        print("Analysis Result (truncated):", str(analysis_result)[:500], "...\n")

        if not analysis_result or "error" in analysis_result:
            print("Analyst failed:", analysis_result)
            return

        # Step 3: Advise
        print("=== Agent 3: Advisor ===")
        advice_result = advisor.process(crawl_result, analysis_result)
        print("Advice Result (truncated):", str(advice_result)[:500], "...\n")

        if not advice_result or "error" in advice_result:
            print("Advisor failed:", advice_result)
            return

        # Final output
        print("\n=== Final Opportunity Analysis ===")
        print(advice_result)

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        import traceback
        print("\nFull traceback:")
        print(traceback.format_exc())

if __name__ == "__main__":
    main() 