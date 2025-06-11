from typing import Dict, Any, Optional, List
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from .base_agent import BaseAgent
import unicodedata
import string
import os
import sys
import time
import spacy
from collections import defaultdict
from googlesearch import search
import random
from ..config.crawler_config import (
    SEARCH_SETTINGS,
    URL_SCORING,
    WEBSITE_PATTERNS,
    SEARCH_QUERIES,
    BIOTECH_DOMAINS,
    NEWS_DOMAINS,
    REQUEST_SETTINGS
)

class CrawlerAgent(BaseAgent):
    """Agent responsible for extracting pipeline and deal information from websites."""
    
    def __init__(self):
        super().__init__("CrawlerAgent")
        self.session = requests.Session()
        self.session.headers.update(REQUEST_SETTINGS["headers"])
        
        # Load spaCy model for entity recognition
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Downloading spaCy model...")
            import subprocess
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        # Enhanced pharmaceutical terms and patterns
        self.pharma_terms = {
            "phases": {
                "Phase I": r"Phase\s*I|Phase\s*1|Phase\s*I/II|Phase\s*1/2",
                "Phase II": r"Phase\s*II|Phase\s*2|Phase\s*II/III|Phase\s*2/3",
                "Phase III": r"Phase\s*III|Phase\s*3",
                "Pre-clinical": r"Pre-?clinical|Preclinical|Pre-IND",
                "IND": r"IND[\s-]*enabled|Investigational\s*New\s*Drug|IND\s*application",
                "Approved": r"Approved|FDA\s*approved|EMA\s*approved|Marketing\s*Authorization"
            },
            "deal_types": {
                "partnership": r"partnership|collaboration|alliance|co-?development|joint\s*venture",
                "license": r"license|licensing|royalty|milestone|technology\s*transfer",
                "acquisition": r"acquire|acquisition|merger|takeover|purchase",
                "investment": r"investment|funding|financing|series\s*[A-F]|venture\s*capital"
            },
            "indications": {
                "cancer": r"cancer|oncology|tumor|malignant|metastatic",
                "autoimmune": r"autoimmune|inflammation|rheumatoid|arthritis|lupus",
                "neurological": r"neurological|CNS|brain|spinal|nerve",
                "infectious": r"infectious|viral|bacterial|fungal|pathogen",
                "rare_disease": r"rare\s*disease|orphan\s*drug|genetic\s*disorder"
            }
        }
        
        # Common biotech/pharma website patterns
        self.website_patterns = [
            "pipeline",
            "products",
            "research",
            "development",
            "press-releases",
            "news",
            "investors",
            "about"
        ]

    def _make_request_with_retry(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with retry logic and better error handling."""
        for attempt in range(REQUEST_SETTINGS["max_retries"]):
            try:
                print(f"\nAttempt {attempt + 1} of {REQUEST_SETTINGS['max_retries']}")
                # Add random delay between attempts
                if attempt > 0:
                    time.sleep(random.uniform(2, 4))
                
                # Rotate User-Agent
                user_agents = [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15'
                ]
                self.session.headers['User-Agent'] = random.choice(user_agents)
                
                response = self.session.get(url, timeout=REQUEST_SETTINGS["timeout"])
                
                # Handle 403 errors specifically
                if response.status_code == 403:
                    print(f"Received 403 error, trying with different headers...")
                    # Try with different headers
                    self.session.headers.update({
                        'Accept': '*/*',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Referer': 'https://www.google.com/',
                        'Origin': 'https://www.google.com',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                    })
                    continue
                
                return response
                
            except requests.exceptions.Timeout:
                print(f"Timeout on attempt {attempt + 1}")
                if attempt == REQUEST_SETTINGS["max_retries"] - 1:
                    return None
                time.sleep(2 ** attempt)
            except requests.exceptions.ConnectionError as e:
                print(f"Connection error on attempt {attempt + 1}: {str(e)}")
                if attempt == REQUEST_SETTINGS["max_retries"] - 1:
                    return None
                time.sleep(2 ** attempt)
            except requests.exceptions.RequestException as e:
                print(f"Request error on attempt {attempt + 1}: {str(e)}")
                if attempt == REQUEST_SETTINGS["max_retries"] - 1:
                    return None
                time.sleep(2 ** attempt)
        
        return None

    def process(self, input_data: str) -> Dict[str, Any]:
        """Process a URL or company name to extract pipeline/deal information."""
        try:
            print(f"\n=== Processing Input: {input_data} ===")
            
            if self._is_url(input_data):
                return self._process_url(input_data)
            else:
                return self._process_company_name(input_data)
                
        except Exception as e:
            print(f"Error processing input: {str(e)}")
            return {"error": f"Error processing input: {str(e)}"}

    def _process_url(self, url: str) -> Dict[str, Any]:
        """Process a URL to extract information."""
        try:
            response = self._make_request_with_retry(url)
            if response is None:
                return {"error": "Failed to fetch URL after multiple attempts"}
            
            if response.status_code != 200:
                return {"error": f"Failed to fetch URL. Status code: {response.status_code}"}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            raw_text = self._extract_text_content(soup)
            
            # Extract structured data
            structured_data = self._extract_structured_data(raw_text)
            
            # Extract entities
            entities = self._extract_entities(raw_text)
            
            return {
                "source_url": url,
                "pipeline_info": {
                    "phases": structured_data["phases"],
                    "indications": structured_data["indications"]
                },
                "deal_info": {
                    "partnerships": structured_data["deals"].get("partnership", []),
                    "licenses": structured_data["deals"].get("license", []),
                    "acquisitions": structured_data["deals"].get("acquisition", []),
                    "investments": structured_data["deals"].get("investment", [])
                },
                "entities": entities,
                "raw_text": raw_text
            }
            
        except Exception as e:
            return {"error": f"Error processing URL: {str(e)}"}

    def _clean_common_artifacts(self, text: str) -> str:
        """Remove common artifacts from press releases."""
        # Remove common press release artifacts
        artifacts = [
            r'FOR IMMEDIATE RELEASE',
            r'FOR RELEASE UPON RECEIPT',
            r'CONTACT:.*?\n',
            r'Media Contact:.*?\n',
            r'Investor Contact:.*?\n',
            r'About.*?Company.*?\n',
            r'Forward-Looking Statements.*?\n',
            r'SOURCE:.*?\n',
            r'©.*?\n',
            r'All rights reserved.*?\n'
        ]
        for pattern in artifacts:
            text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
        return text

    def _remove_boilerplate_sections(self, text: str) -> str:
        """Remove boilerplate sections from press releases."""
        # Common boilerplate sections to remove
        sections = [
            r'About the Company.*?(?=\n\n|\Z)',
            r'Forward-Looking Statements.*?(?=\n\n|\Z)',
            r'Investor Relations.*?(?=\n\n|\Z)',
            r'Media Relations.*?(?=\n\n|\Z)',
            r'Legal Notice.*?(?=\n\n|\Z)'
        ]
        for pattern in sections:
            text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
        return text

    def _extract_relevant_sections(self, text: str) -> str:
        """Extract relevant sections from press releases."""
        # Look for sections that typically contain important information
        relevant_sections = []
        
        # Look for sections with key terms
        key_terms = [
            r'clinical trial',
            r'phase [123]',
            r'regulatory',
            r'approval',
            r'partnership',
            r'collaboration',
            r'license',
            r'acquisition'
        ]
        
        # Split text into paragraphs
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            # Check if paragraph contains any key terms
            if any(re.search(term, paragraph, re.IGNORECASE) for term in key_terms):
                relevant_sections.append(paragraph)
        
        return '\n\n'.join(relevant_sections) if relevant_sections else text

    def _truncate_text(self, text: str, max_words: int = 500) -> str:
        """Truncate text to a maximum number of words."""
        words = text.split()
        if len(words) > max_words:
            return ' '.join(words[:max_words]) + '...'
        return text

    def preprocess_press_release(self, text: str) -> str:
        """Preprocess press release text to extract relevant information."""
        import re, unicodedata

        text = unicodedata.normalize('NFKD', text)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'&[a-z]+;', ' ', text)
        text = self._clean_common_artifacts(text)
        text = self._remove_boilerplate_sections(text)
        text = ' '.join(text.split())
        text = self._extract_relevant_sections(text)
        text = self._truncate_text(text, max_words=500)
        return text.strip()
    
    def _extract_structured_data(self, text: str) -> Dict[str, Any]:
        """Extract structured data from text."""
        structured_data = {
            "phases": defaultdict(list),
            "indications": defaultdict(list),
            "deals": defaultdict(list)
        }
        
        # Extract phase information
        for phase, pattern in self.pharma_terms["phases"].items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context = self._get_context(text, match.start(), 200)
                drug_name = self._extract_drug_name(context)
                indication = self._extract_indication(context)
                
                structured_data["phases"][phase].append({
                    "drug_name": drug_name,
                    "indication": indication,
                    "context": context
                })
        
        # Extract deal information
        for deal_type, pattern in self.pharma_terms["deal_types"].items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context = self._get_context(text, match.start(), 200)
                partner = self._extract_partner(context)
                
                structured_data["deals"][deal_type].append({
                    "partner": partner,
                    "context": context
                })
        
        # Extract indications
        for indication_type, pattern in self.pharma_terms["indications"].items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context = self._get_context(text, match.start(), 200)
                structured_data["indications"][indication_type].append({
                    "context": context
                })
        
        return structured_data

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text using spaCy."""
        doc = self.nlp(text)
        entities = defaultdict(list)
        
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "GPE", "PRODUCT"]:
                entities[ent.label_].append(ent.text)
        
        return dict(entities)

    def _get_context(self, text: str, position: int, window: int = 200) -> str:
        """Get context around a position in text."""
        start = max(0, position - window)
        end = min(len(text), position + window)
        return text[start:end].strip()

    def _extract_drug_name(self, context: str) -> str:
        """Extract drug name from context."""
        # Look for common drug name patterns
        patterns = [
            r'([A-Z][a-z]+-[0-9]+)',  # e.g., Drug-123
            r'([A-Z][a-z]+[0-9]+)',   # e.g., Drug123
            r'([A-Z]{2,}-[0-9]+)',    # e.g., DR-123
            r'([A-Z]{2,}[0-9]+)'      # e.g., DR123
        ]
        
        for pattern in patterns:
            match = re.search(pattern, context)
            if match:
                return match.group(1)
        
        return "Unknown"

    def _extract_partner(self, context: str) -> str:
        """Extract partner company name from context."""
        # Look for company names after "with" or "by"
        match = re.search(r'(?:with|by)\s+([A-Z][a-zA-Z\s&]+(?:Inc\.|LLC|Ltd\.|Corp\.)?)', context)
        if match:
            return match.group(1).strip()
        return "Partner Company"

    def _extract_indication(self, context: str) -> str:
        """Extract indication from context."""
        # Look for indication after "for" or "in"
        match = re.search(r'(?:for|in)\s+([^.,]+)', context)
        if match:
            return match.group(1).strip()
        return "Unknown"

    def _find_company_urls(self, company_name: str) -> List[str]:
        """Find company URLs using Google search, focusing on press releases and news."""
        print(f"\nSearching for {company_name} press releases and news...")
        urls = []
        
        for query_template in SEARCH_QUERIES:
            query = query_template.format(company=company_name)
            try:
                print(f"Trying search query: {query}")
                # Search with a random delay to avoid rate limiting
                time.sleep(random.uniform(
                    SEARCH_SETTINGS["delay"]["min"],
                    SEARCH_SETTINGS["delay"]["max"]
                ))
                search_results = search(query, num_results=SEARCH_SETTINGS["num_results"])
                
                for url in search_results:
                    if url not in urls:
                        urls.append(url)
                        print(f"Found URL: {url}")
                
            except Exception as e:
                print(f"Error during search: {str(e)}")
                continue
        
        return urls

    def _find_best_url(self, urls: List[str], company_name: str) -> Optional[str]:
        """Find the best URL from the list of URLs, prioritizing press releases and news."""
        if not urls:
            return None
        
        # Score each URL based on relevance
        scored_urls = []
        for url in urls:
            score = 0
            domain = urlparse(url).netloc.lower()
            
            # Check if it's a news domain
            if any(news_domain in domain for news_domain in NEWS_DOMAINS):
                score += URL_SCORING["news_domain"]
            
            # Check for press release patterns
            if any(pattern in url.lower() for pattern in ["press-release", "press-release", "news", "media"]):
                score += URL_SCORING["press_release"]
            
            # Check if it's the company's main domain
            if company_name.lower() in domain:
                score += URL_SCORING["company_domain"]
            
            # Check for pipeline-related pages
            for pattern in WEBSITE_PATTERNS:
                if pattern in url.lower():
                    score += URL_SCORING["pipeline_page"]
            
            # Check for common biotech/pharma domains
            if any(x in domain for x in BIOTECH_DOMAINS):
                score += URL_SCORING["biotech_domain"]
            
            scored_urls.append((url, score))
        
        # Sort by score and return the highest scoring URL
        scored_urls.sort(key=lambda x: x[1], reverse=True)
        return scored_urls[0][0] if scored_urls else None

    def _process_company_name(self, company_name: str) -> Dict[str, Any]:
        """Process a company name to find and extract information."""
        print(f"\n=== Processing Company Name: {company_name} ===")
        
        # Normalize company name
        normalized_name = self._normalize_company_name(company_name)
        print(f"Normalized company name: {normalized_name}")
        
        # Find company URLs
        urls = self._find_company_urls(normalized_name)
        if not urls:
            print("No URLs found for company")
            return {"error": "No URLs found"}
        
        # Try each URL until we get a successful response
        for url in urls:
            print(f"\nTrying URL: {url}")
            response = self._make_request_with_retry(url)
            
            if response and response.status_code == 200:
                print(f"Successfully fetched URL: {url}")
                return self._extract_information(response.text, url)
            else:
                print(f"Failed to fetch URL: {url}")
                continue
        
        return {"error": "Failed to fetch any URLs"}

    def _normalize_company_name(self, company_name: str) -> str:
        """Normalize company name for better matching."""
        # Remove common suffixes
        suffixes = ['Inc.', 'Inc', 'LLC', 'Ltd.', 'Ltd', 'Corp.', 'Corp', 'PLC', 'plc']
        name = company_name
        for suffix in suffixes:
            name = name.replace(suffix, '').strip()
        
        # Remove special characters and normalize spaces
        name = re.sub(r'[^\w\s]', '', name)
        name = ' '.join(name.split())
        
        return name
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract relevant text content from the webpage."""
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
    
    def _is_url(self, text: str) -> bool:
        """Check if the input is a valid URL."""
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc])
        except:
            return False

    def clean_html(self, raw_html):
        """Clean HTML content by removing noise and normalizing text."""
        soup = BeautifulSoup(raw_html, "html.parser")
        
        # Remove common noise elements
        for noise in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
            noise.decompose()
        
        # Remove elements with common noise text
        noise_patterns = [
            'skip to main content',
            'skip to content',
            'menu',
            'navigation',
            'cookie notice',
            'privacy policy'
        ]
        
        for element in soup.find_all(string=True):
            if any(pattern in element.lower() for pattern in noise_patterns):
                element.parent.decompose()
        
        # Get text and normalize
        text = soup.get_text()
        # Strip whitespace and normalize spaces
        text = ' '.join(text.split())
        return text.strip()

    def _extract_information(self, html_content: str, url: str) -> Dict[str, Any]:
        """Extract information from HTML content."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text(separator=' ', strip=True)
            
            # Extract information
            pipeline_info = self._extract_pipeline_info(text)
            deal_info = self._extract_deal_info(text)
            entities = self._extract_entities(text)
            
            return {
                "url": url,
                "pipeline_info": pipeline_info,
                "deal_info": deal_info,
                "entities": entities
            }
            
        except Exception as e:
            print(f"Error extracting information: {str(e)}")
            return {"error": str(e)}

    def _extract_pipeline_info(self, text: str) -> Dict[str, List[Dict[str, str]]]:
        """Extract pipeline information from text."""
        pipeline_info = defaultdict(list)
        
        # Extract phase information
        for phase, pattern in self.pharma_terms["phases"].items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get context around the match
                start = max(0, match.start() - 200)
                end = min(len(text), match.end() + 200)
                context = text[start:end]
                
                # Extract drug name and indication
                drug_match = re.search(r'([A-Za-z0-9-]+(?:\s*[A-Za-z0-9-]+)*)', context)
                drug = drug_match.group(1) if drug_match else "Unknown"
                
                indication_match = re.search(r'for\s+([^.,]+)', context)
                indication = indication_match.group(1) if indication_match else "Unknown"
                
                # Only add if we found something meaningful
                if drug != "Unknown" or indication != "Unknown":
                    pipeline_info[phase].append({
                        "drug": drug,
                        "indication": indication,
                        "context": context.strip()
                    })
        
        return dict(pipeline_info)

    def _extract_deal_info(self, text: str) -> Dict[str, List[Dict[str, str]]]:
        """Extract deal information from text."""
        deal_info = defaultdict(list)
        
        # Extract deal information
        for deal_type, pattern in self.pharma_terms["deal_types"].items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get context around the match
                start = max(0, match.start() - 200)
                end = min(len(text), match.end() + 200)
                context = text[start:end]
                
                # Extract partner name
                partner_match = re.search(r'with\s+([A-Za-z0-9\s]+)', context)
                partner = partner_match.group(1) if partner_match else "Partner Company"
                
                # Only add if we found something meaningful
                if partner != "Partner Company":
                    deal_info[deal_type].append({
                        "partner": partner,
                        "context": context.strip()
                    })
        
        return dict(deal_info) 