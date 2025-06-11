from typing import Dict, Any, Optional
import json
from pathlib import Path
import jinja2
from weasyprint import HTML
import logging
from datetime import datetime
from src.config.model_config import TOOL_CONFIGS, PATHS

logger = logging.getLogger(__name__)

class ReportFormatter:
    """Tool for formatting reports in various formats."""
    
    def __init__(self):
        self.config = TOOL_CONFIGS["formatter"]
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.config["template_path"])
        )
    
    def format_report(
        self,
        data: Dict[str, Any],
        output_format: str = "json",
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Format report in specified format.
        
        Args:
            data: Report data to format
            output_format: Desired output format (json, pdf, html)
            output_path: Path to save output file
            
        Returns:
            Dict containing formatted report
        """
        if output_format not in self.config["output_formats"]:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        if output_format == "json":
            return self._format_json(data, output_path)
        elif output_format == "pdf":
            return self._format_pdf(data, output_path)
        elif output_format == "html":
            return self._format_html(data, output_path)
    
    def _format_json(self, data: Dict[str, Any], output_path: Optional[str]) -> Dict[str, Any]:
        """Format report as JSON.
        
        Args:
            data: Report data
            output_path: Path to save JSON file
            
        Returns:
            Formatted JSON data
        """
        formatted_data = {
            "report": data,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "format": "json"
            }
        }
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(formatted_data, f, indent=2)
        
        return formatted_data
    
    def _format_pdf(self, data: Dict[str, Any], output_path: Optional[str]) -> Dict[str, Any]:
        """Format report as PDF.
        
        Args:
            data: Report data
            output_path: Path to save PDF file
            
        Returns:
            Dict containing PDF data
        """
        # Load HTML template
        template = self.template_env.get_template("report.html")
        
        # Render template with data
        html_content = template.render(
            report=data,
            generated_at=datetime.now().isoformat()
        )
        
        # Convert HTML to PDF
        pdf = HTML(string=html_content).write_pdf()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf)
        
        return {
            "content": pdf,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "format": "pdf"
            }
        }
    
    def _format_html(self, data: Dict[str, Any], output_path: Optional[str]) -> Dict[str, Any]:
        """Format report as HTML.
        
        Args:
            data: Report data
            output_path: Path to save HTML file
            
        Returns:
            Dict containing HTML data
        """
        # Load HTML template
        template = self.template_env.get_template("report.html")
        
        # Render template with data
        html_content = template.render(
            report=data,
            generated_at=datetime.now().isoformat()
        )
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(html_content)
        
        return {
            "content": html_content,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "format": "html"
            }
        }
    
    def create_one_page_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a one-page summary of the report.
        
        Args:
            data: Full report data
            
        Returns:
            One-page summary data
        """
        return {
            "executive_summary": data.get("executive_summary", ""),
            "key_findings": {
                "therapeutic_areas": data.get("therapeutic_areas", []),
                "mechanisms_of_action": data.get("mechanisms_of_action", []),
                "market_potential": data.get("market_analysis", {}).get("market_potential", ""),
                "key_risks": data.get("risk_assessment", {}).get("key_risks", [])
            },
            "recommendations": data.get("recommendations", {}).get("next_steps", []),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "format": "summary"
            }
        } 