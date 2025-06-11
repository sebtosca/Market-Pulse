from typing import Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import logging
from src.config.model_config import TOOL_CONFIGS

logger = logging.getLogger(__name__)

class ScraperTool:
    """Tool for scraping content from websites and press releases."""
    
    def __init__(self):
        self.config = TOOL_CONFIGS["scraper"]
        self.headers = {
            "User-Agent": self.config["user_agent"]
        }
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape content from a URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dict containing scraped content and metadata
        """
        try:
            # First try using newspaper3k
            article = Article(url)
            article.download()
            article.parse()
            
            # If newspaper3k fails, fall back to BeautifulSoup
            if not article.text:
                response = requests.get(url, headers=self.headers, timeout=self.config["timeout"])
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract text content
                text = self._extract_text_content(soup)
                
                return {
                    "url": url,
                    "title": soup.title.string if soup.title else "",
                    "text": text,
                    "html": response.text,
                    "metadata": self._extract_metadata(soup)
                }
            
            return {
                "url": url,
                "title": article.title,
                "text": article.text,
                "html": article.html,
                "metadata": {
                    "authors": article.authors,
                    "publish_date": article.publish_date,
                    "keywords": article.keywords,
                    "summary": article.summary
                }
            }
            
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            return {
                "url": url,
                "error": str(e)
            }
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract text content from BeautifulSoup object.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Extracted text content
        """
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading and trailing space
        lines = (line.strip() for line in text.splitlines())
        
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from BeautifulSoup object.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dict containing metadata
        """
        metadata = {}
        
        # Extract meta tags
        for meta in soup.find_all("meta"):
            if meta.get("name"):
                metadata[meta["name"]] = meta.get("content", "")
            elif meta.get("property"):
                metadata[meta["property"]] = meta.get("content", "")
        
        # Extract structured data
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                import json
                metadata["structured_data"] = json.loads(script.string)
            except:
                pass
        
        return metadata
    
    def extract_pipeline_info(self, text: str) -> Dict[str, Any]:
        """Extract pipeline information from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict containing pipeline information
        """
        # TODO: Implement more sophisticated pipeline information extraction
        return {
            "products": [],
            "phases": {},
            "indications": []
        }
    
    def extract_deal_info(self, text: str) -> Dict[str, Any]:
        """Extract deal information from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict containing deal information
        """
        # TODO: Implement more sophisticated deal information extraction
        return {
            "partnerships": [],
            "licenses": [],
            "acquisitions": []
        } 