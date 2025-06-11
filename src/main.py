from typing import Dict, Any
import argparse
import json
from pathlib import Path
from agents.crawler import CrawlerAgent
from agents.analyst import AnalystAgent
from agents.advisor import AdvisorAgent

def save_report(report: Dict[str, Any], output_path: str) -> None:
    """Save the generated report to a file.
    
    Args:
        report: The report to save
        output_path: Path where to save the report
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

def process_opportunity(input_data: str, output_path: str) -> None:
    """Process an opportunity through the agent pipeline.
    
    Args:
        input_data: URL or company name to analyze
        output_path: Path where to save the report
    """
    # Initialize agents
    crawler = CrawlerAgent()
    analyst = AnalystAgent()
    advisor = AdvisorAgent()
    
    # Step 1: Extract information
    print("Step 1: Extracting information...")
    extracted_info = crawler.process(input_data)
    
    if "error" in extracted_info:
        print(f"Error in extraction: {extracted_info['error']}")
        return
    
    # Step 2: Analyze information
    print("Step 2: Analyzing information...")
    analysis = analyst.process(extracted_info)
    
    if "error" in analysis:
        print(f"Error in analysis: {analysis['error']}")
        return
    
    # Step 3: Generate report
    print("Step 3: Generating report...")
    report = advisor.process(analysis)
    
    if "error" in report:
        print(f"Error in report generation: {report['error']}")
        return
    
    # Save report
    save_report(report, output_path)
    print(f"Report saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Business Development Opportunity Analysis System")
    parser.add_argument("input", help="URL or company name to analyze")
    parser.add_argument("--output", "-o", default="reports/opportunity_report.json",
                      help="Path where to save the report (default: reports/opportunity_report.json)")
    
    args = parser.parse_args()
    process_opportunity(args.input, args.output)

if __name__ == "__main__":
    main() 