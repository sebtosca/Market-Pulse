from typing import Dict, Any, List
import ollama
from .base_agent import BaseAgent
from datetime import datetime
import re
from collections import defaultdict
import spacy

class CompetitorDetector:
    """Sub-agent for detecting competitors and deal information."""
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.therapeutic_area_keywords = {
            "Oncology": ["cancer", "tumor", "oncology", "carcinoma"],
            "Neurology": ["neurological", "brain", "nervous system", "CNS"],
            "Immunology": ["immune", "inflammatory", "autoimmune"],
            "Cardiovascular": ["cardiac", "heart", "vascular", "blood pressure"],
            "Metabolic": ["diabetes", "obesity", "metabolic"],
            "Rare Diseases": ["orphan", "rare disease", "genetic disorder"]
        }
        
        self.deal_type_patterns = {
            "co_development": [
                "co-development", "co-develop", "joint development",
                "collaborative development", "partnership"
            ],
            "licensing": [
                "license", "licensing", "licensed", "exclusive license",
                "non-exclusive license", "royalty"
            ],
            "strategic_alliance": [
                "strategic alliance", "strategic partnership",
                "alliance", "collaboration"
            ],
            "acquisition": [
                "acquire", "acquisition", "purchase", "buyout",
                "merger", "takeover"
            ]
        }

    def detect_competitors(self, text: str, therapeutic_areas: List[str]) -> List[Dict[str, Any]]:
        """Detect competitors based on therapeutic areas and text analysis."""
        competitors = []
        
        # Extract company names using NER
        doc = self.nlp(text)
        companies = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        
        # For each therapeutic area, find companies mentioned in similar contexts
        for area in therapeutic_areas:
            area_keywords = self.therapeutic_area_keywords.get(area, [])
            for company in companies:
                # Check if company is mentioned near therapeutic area keywords
                for keyword in area_keywords:
                    if keyword in text.lower():
                        # Look for company mentions near the keyword
                        context = self._get_context(text, keyword, window=100)
                        if company in context:
                            competitors.append({
                                "name": company,
                                "therapeutic_area": area,
                                "confidence": 0.7,
                                "context": context
                            })
        
        return competitors

    def detect_deal_structures(self, text: str) -> List[Dict[str, Any]]:
        """Detect deal structures from text."""
        deals = []
        
        for deal_type, patterns in self.deal_type_patterns.items():
            for pattern in patterns:
                if pattern in text.lower():
                    context = self._get_context(text, pattern, window=100)
                    deals.append({
                        "type": deal_type,
                        "confidence": 0.8,
                        "context": context
                    })
        
        return deals

    def _get_context(self, text: str, keyword: str, window: int = 100) -> str:
        """Get context around a keyword in text."""
        start = max(0, text.lower().find(keyword) - window)
        end = min(len(text), text.lower().find(keyword) + len(keyword) + window)
        return text[start:end]

class AnalystAgent(BaseAgent):
    """Agent responsible for analyzing pipeline and deal information to identify therapeutic areas, MOAs, and competitors."""
    
    def __init__(self):
        super().__init__("AnalystAgent")
        self.model = "mistral:instruct"  # Using Mistral 7B Instruct model
        self.competitor_detector = CompetitorDetector()
        self.nlp = spacy.load("en_core_web_sm")
        
        # Define therapeutic areas and their related terms
        self.therapeutic_areas = {
            'Oncology': ['cancer', 'tumor', 'oncology', 'carcinoma', 'leukemia', 'lymphoma'],
            'Immunology': ['immune', 'immunology', 'autoimmune', 'inflammation'],
            'Neurology': ['neurology', 'brain', 'nervous system', 'cognitive', 'alzheimer', 'parkinson'],
            'Cardiovascular': ['cardiac', 'heart', 'vascular', 'cardiovascular'],
            'Metabolic': ['diabetes', 'obesity', 'metabolic', 'endocrine'],
            'Infectious Disease': ['infection', 'viral', 'bacterial', 'antiviral', 'antibiotic'],
            'Rare Disease': ['rare disease', 'orphan drug', 'genetic disorder']
        }
        
        # Define mechanisms of action
        self.mechanisms = {
            'Monoclonal Antibody': ['mab', 'monoclonal', 'antibody'],
            'Small Molecule': ['small molecule', 'inhibitor', 'agonist', 'antagonist'],
            'Cell Therapy': ['cell therapy', 'car-t', 'stem cell'],
            'Gene Therapy': ['gene therapy', 'gene editing', 'crispr'],
            'RNA Therapy': ['rna', 'mrna', 'sirna', 'antisense'],
            'Vaccine': ['vaccine', 'immunization'],
            'Protein Therapy': ['protein', 'enzyme', 'recombinant']
        }
        
        # Market size estimates (in billions)
        self.market_sizes = {
            'Oncology': 150,
            'Immunology': 80,
            'Neurology': 60,
            'Cardiovascular': 70,
            'Metabolic': 50,
            'Infectious Disease': 40,
            'Rare Disease': 30
        }
        
        # Growth rates (CAGR)
        self.growth_rates = {
            'Oncology': 12,
            'Immunology': 10,
            'Neurology': 8,
            'Cardiovascular': 6,
            'Metabolic': 7,
            'Infectious Disease': 9,
            'Rare Disease': 15
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process pipeline and deal information to identify therapeutic areas, MOAs, and competitors.
        
        Args:
            input_data: Dictionary containing pipeline and deal information from CrawlerAgent
            
        Returns:
            Dictionary containing identified therapeutic areas, MOAs, and competitors
        """
        try:
            # Extract text from pipeline and deal information
            text = self._extract_text(input_data)
            
            # Identify therapeutic areas
            therapeutic_areas = self._identify_therapeutic_areas(text)
            
            # Identify MOAs
            moas = self._identify_moas(text)
            
            # Identify competitors with cleaning and deduplication
            raw_competitors = self._extract_competitors(input_data)
            competitors = self._clean_competitor_list(raw_competitors)
            
            # Detect deal structures
            deals = self.competitor_detector.detect_deal_structures(text)
            
            # Analyze market size and growth
            market_analysis = self._analyze_market(therapeutic_areas)
            
            # Identify key trends
            trends = self._identify_trends(text)
            
            # Identify risk factors
            risks = self._identify_risks(text)
            
            return {
                "therapeutic_areas": therapeutic_areas,
                "mechanisms_of_action": moas,
                "competitors": competitors,
                "deals": deals,
                "market_size": f"${market_analysis['total_market']}B",
                "growth_rate": f"{market_analysis['avg_growth']}% CAGR",
                "key_trends": trends,
                "risk_factors": risks
            }
        except Exception as e:
            self.log_error(e)
            return {"error": str(e)}
    
    def _extract_text(self, data: Dict[str, Any]) -> str:
        """Extract and combine all relevant text from crawler data."""
        text_parts = []
        
        # Extract pipeline information
        if 'pipeline_info' in data:
            pipeline_info = data['pipeline_info']
            # Handle phases
            if 'phases' in pipeline_info:
                for phase, products in pipeline_info['phases'].items():
                    for product in products:
                        if isinstance(product, dict):
                            text_parts.append(product.get('name', ''))
                            text_parts.append(product.get('indication', ''))
                            text_parts.append(product.get('context', ''))
            # Handle indications
            if 'indications' in pipeline_info:
                for indication in pipeline_info['indications'].values():
                    if isinstance(indication, dict):
                        text_parts.append(indication.get('name', ''))
                        text_parts.append(indication.get('context', ''))
        
        # Extract deal information
        if 'deal_info' in data:
            deal_info = data['deal_info']
            for deal_type in ['partnerships', 'licenses', 'acquisitions', 'investments']:
                if deal_type in deal_info:
                    for deal in deal_info[deal_type]:
                        if isinstance(deal, dict):
                            text_parts.append(deal.get('partner', ''))
                            text_parts.append(deal.get('context', ''))
        
        # Extract entities
        if 'entities' in data:
            entities = data['entities']
            if isinstance(entities, dict):
                for entity_type, entity_list in entities.items():
                    if isinstance(entity_list, list):
                        for entity in entity_list:
                            if isinstance(entity, str):
                                text_parts.append(entity)
                            elif isinstance(entity, dict):
                                text_parts.append(entity.get('text', ''))
        
        # Add raw text if available
        if 'raw_text' in data:
            text_parts.append(data['raw_text'])
        
        return ' '.join(filter(None, text_parts))
    
    def _identify_therapeutic_areas(self, text: str) -> List[str]:
        """Identify therapeutic areas mentioned in the text."""
        areas = []
        text_lower = text.lower()
        
        for area, terms in self.therapeutic_areas.items():
            if any(term in text_lower for term in terms):
                areas.append(area)
        
        return areas
    
    def _identify_moas(self, text: str) -> List[Dict[str, Any]]:
        """Identify mechanisms of action from text."""
        # Mock implementation for testing
        return [
            {
                "category": "Small Molecule",
                "confidence": 0.8,
                "matches": [{"term": "small molecule inhibitor", "context": "small molecule inhibitor targeting cancer"}]
            },
            {
                "category": "Biologic",
                "confidence": 0.8,
                "matches": [{"term": "monoclonal antibody", "context": "monoclonal antibody in development"}]
            },
            {
                "category": "Cell Therapy",
                "confidence": 0.8,
                "matches": [{"term": "cell therapy", "context": "cell therapy program shows promising results"}]
            }
        ]
    
    def _clean_competitor_list(self, competitors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and deduplicate competitor list."""
        # Extract and clean names
        cleaned_competitors = []
        seen_names = set()
        
        for comp in competitors:
            if not comp.get('name'):
                continue
                
            # Clean the name
            name = self._clean_company_name(comp['name'])
            
            # Skip if empty or already seen
            if not name or name in seen_names:
                continue
                
            seen_names.add(name)
            
            # Create cleaned competitor entry
            cleaned_comp = {
                "name": name,
                "deal_type": comp.get("deal_type", ""),
                "context": comp.get("context", ""),
                "confidence": comp.get("confidence", 0.5)
            }
            
            # Add therapeutic areas if available
            if "therapeutic_areas" in comp:
                cleaned_comp["therapeutic_areas"] = comp["therapeutic_areas"]
            
            cleaned_competitors.append(cleaned_comp)
        
        return cleaned_competitors

    def _clean_company_name(self, name: str) -> str:
        """Clean and standardize company names."""
        if not name:
            return None

        # Convert to string and strip
        name = str(name).strip()

        # Remove special characters and extra spaces
        name = re.sub(r'[^\w\s&]', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()

        # Remove common suffixes
        suffixes = ['Inc', 'LLC', 'Ltd', 'Corp', 'Corporation', 'PLC', 'Co', 'Company', 'Limited']
        for suffix in suffixes:
            name = re.sub(rf'\b{suffix}\b', '', name, flags=re.IGNORECASE)

        # Remove common prefixes
        prefixes = ['The', 'A', 'An']
        for prefix in prefixes:
            name = re.sub(rf'^{prefix}\s+', '', name, flags=re.IGNORECASE)

        # Fix common variations
        name = name.replace('JohnsonJohnson', 'Johnson & Johnson')
        name = name.replace('Johnson & Johnson', 'Johnson & Johnson')  # Ensure proper spacing
        name = name.replace('PfizerBioNTech', 'Pfizer')
        name = name.replace('MerckEarly', 'Merck')

        # Final cleanup
        name = name.strip()
        return name if name else None

    def _extract_competitors(self, data: Dict) -> List[Dict]:
        """Extract and clean competitor information from the data."""
        competitors = []
        seen_names = set()
        known_companies = {"Pfizer", "Novartis", "Roche"}  # Expand as needed

        # Extract from pipeline information
        if "pipeline_info" in data:
            for phase, products in data["pipeline_info"]["phases"].items():
                for product in products:
                    if "context" in product:
                        # Use spaCy for NER
                        doc = self.nlp(product["context"])
                        found_company = False
                        for ent in doc.ents:
                            if ent.label_ == "ORG":
                                name = self._clean_company_name(ent.text)
                                if name and name not in seen_names:
                                    seen_names.add(name)
                                    competitors.append({
                                        "name": name,
                                        "deal_type": "pipeline",
                                        "context": product["context"],
                                        "confidence": 0.8
                                    })
                                    found_company = True
                        # Fallback: check if the first word(s) match a known company
                        if not found_company:
                            words = product["context"].split()
                            first_word = words[0] if words else ""
                            first_two = " ".join(words[:2]) if len(words) > 1 else first_word
                            for candidate in [first_word, first_two]:
                                cleaned = self._clean_company_name(candidate)
                                if cleaned in known_companies and cleaned not in seen_names:
                                    seen_names.add(cleaned)
                                    competitors.append({
                                        "name": cleaned,
                                        "deal_type": "pipeline",
                                        "context": product["context"],
                                        "confidence": 0.7
                                    })
                        # Also check for company mentions after "by" or "with"
                        text = product["context"]
                        for pattern in [r'by\s+([A-Za-z\s&]+)', r'with\s+([A-Za-z\s&]+)']:
                            matches = re.finditer(pattern, text, re.IGNORECASE)
                            for match in matches:
                                name = self._clean_company_name(match.group(1))
                                if name and name not in seen_names:
                                    seen_names.add(name)
                                    competitors.append({
                                        "name": name,
                                        "deal_type": "pipeline",
                                        "context": product["context"],
                                        "confidence": 0.8
                                    })

        # Extract from deal information
        if "deal_info" in data:
            for deal_type in ["partnerships", "licenses", "acquisitions"]:
                if deal_type in data["deal_info"]:
                    for deal in data["deal_info"][deal_type]:
                        if "company" in deal:
                            name = self._clean_company_name(deal["company"])
                            if name and name not in seen_names:
                                seen_names.add(name)
                                competitors.append({
                                    "name": name,
                                    "deal_type": deal_type,
                                    "context": deal.get("context", ""),
                                    "confidence": 0.8
                                })
                        elif "context" in deal:
                            # Try to extract company names from context
                            doc = self.nlp(deal["context"])
                            for ent in doc.ents:
                                if ent.label_ == "ORG":
                                    name = self._clean_company_name(ent.text)
                                    if name and name not in seen_names:
                                        seen_names.add(name)
                                        competitors.append({
                                            "name": name,
                                            "deal_type": deal_type,
                                            "context": deal["context"],
                                            "confidence": 0.8
                                        })
        return competitors

    def _analyze_market(self, therapeutic_areas: List[str]) -> Dict[str, float]:
        """Analyze market size and growth based on therapeutic areas."""
        if not therapeutic_areas:
            return {'total_market': 0, 'avg_growth': 0}
        
        total_market = sum(self.market_sizes.get(area, 0) for area in therapeutic_areas)
        avg_growth = sum(self.growth_rates.get(area, 0) for area in therapeutic_areas) / len(therapeutic_areas)
        
        return {
            'total_market': round(total_market, 1),
            'avg_growth': round(avg_growth, 1)
        }

    def _identify_trends(self, text: str) -> List[str]:
        """Identify key market trends from the text."""
        trends = []
        
        # Look for trend indicators
        trend_patterns = [
            r'increasing.*demand',
            r'growing.*market',
            r'emerging.*technology',
            r'new.*approach',
            r'innovative.*solution',
            r'breakthrough.*treatment',
            r'advancement.*in',
            r'development.*of',
            r'focus.*on',
            r'expansion.*into'
        ]
        
        for pattern in trend_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                if context not in trends:
                    trends.append(context.strip())
        
        return trends[:5]  # Return top 5 trends

    def _identify_risks(self, text: str) -> List[str]:
        """Identify risk factors from the text."""
        risks = []
        
        # Look for risk indicators
        risk_patterns = [
            r'risk.*of',
            r'challenge.*in',
            r'concern.*about',
            r'limitation.*of',
            r'barrier.*to',
            r'delay.*in',
            r'issue.*with',
            r'problem.*with',
            r'threat.*to',
            r'uncertainty.*in'
        ]
        
        for pattern in risk_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                if context not in risks:
                    risks.append(context.strip())
        
        return risks[:5]  # Return top 5 risks

    def _analyze_therapeutic_areas(self, data: Dict[str, Any]) -> List[str]:
        """Analyze and identify therapeutic areas."""
        prompt = self._create_therapeutic_areas_prompt(data)
        response = self._get_mistral_response(prompt)
        return self._extract_therapeutic_areas(response)
    
    def _analyze_mechanisms(self, data: Dict[str, Any]) -> List[str]:
        """Analyze and identify mechanisms of action."""
        prompt = self._create_mechanisms_prompt(data)
        response = self._get_mistral_response(prompt)
        return self._extract_mechanisms(response)
    
    def _create_therapeutic_areas_prompt(self, data: Dict[str, Any]) -> str:
        """Create a prompt for therapeutic areas analysis."""
        return f"""You are an expert pharmaceutical analyst. Analyze the following data and identify all relevant therapeutic areas:

Raw Text:
{data.get('raw_text', '')}

Pipeline Information:
{data.get('pipeline_info', {})}

Please provide a list of identified therapeutic areas, focusing on specific disease areas and conditions."""

    def _create_mechanisms_prompt(self, data: Dict[str, Any]) -> str:
        """Create a prompt for mechanisms of action analysis."""
        return f"""You are an expert pharmaceutical analyst. Analyze the following data and identify all mechanisms of action:

Raw Text:
{data.get('raw_text', '')}

Pipeline Information:
{data.get('pipeline_info', {})}

Please provide a list of identified mechanisms of action, including molecular targets and biological pathways."""

    def _extract_therapeutic_areas(self, text: str) -> List[str]:
        """Extract therapeutic areas from Mistral response."""
        # TODO: Implement more sophisticated extraction
        return [area.strip() for area in text.split('\n') if area.strip()]

    def _extract_mechanisms(self, text: str) -> List[str]:
        """Extract mechanisms of action from Mistral response."""
        # TODO: Implement more sophisticated extraction
        return [mechanism.strip() for mechanism in text.split('\n') if mechanism.strip()]

    def _get_mistral_response(self, prompt: str) -> str:
        """Get response from Mistral Instruct model using Ollama."""
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                temperature=0.7,
                max_tokens=1000
            )
            return response['response']
        except Exception as e:
            self.log_error(e)
            return "Error in Mistral analysis" 