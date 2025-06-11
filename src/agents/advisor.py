from typing import Dict, Any, List
import ollama
from .base_agent import BaseAgent
import os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

class AdvisorAgent(BaseAgent):
    """Agent responsible for generating a one-page opportunity analysis report for BD teams."""
    
    def __init__(self):
        super().__init__("AdvisorAgent")
        self.model = "openhermes"  # Using OpenHermes 2.5 (Mistral)
        
        self.strategic_frameworks = {
            'immediate_actions': [
                'Engage BD team for partnership discussions',
                'Accelerate clinical development',
                'Expand market access',
                'Strengthen IP portfolio',
                'Optimize manufacturing capacity'
            ],
            'market_entry': [
                'Leverage existing expertise',
                'Consider combination therapies',
                'Explore adjacent markets',
                'Develop companion diagnostics',
                'Build digital health solutions'
            ],
            'risk_mitigation': [
                'Monitor competitive pipeline',
                'Establish contingency plans',
                'Diversify supply chain',
                'Strengthen regulatory strategy',
                'Protect market position'
            ],
            'value_creation': [
                'Strategic acquisitions',
                'Technology partnerships',
                'R&D collaborations',
                'Market expansion',
                'Product lifecycle management'
            ]
        }
        
        self.recommendation_templates = {
            'high_potential': {
                'tone': 'positive',
                'key_points': [
                    'Strong market opportunity',
                    'Competitive advantage',
                    'Clear path to value',
                    'Manageable risks'
                ]
            },
            'moderate_potential': {
                'tone': 'balanced',
                'key_points': [
                    'Solid market position',
                    'Some competitive challenges',
                    'Need for strategic focus',
                    'Risk mitigation required'
                ]
            },
            'high_risk': {
                'tone': 'cautious',
                'key_points': [
                    'Significant challenges',
                    'High competition',
                    'Uncertain market dynamics',
                    'Need for careful evaluation'
                ]
            }
        }

    def process(self, crawler_data: Dict[str, Any], analyst_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process crawler and analyst data to generate strategic recommendations.
        
        Args:
            crawler_data: Dictionary containing pipeline and deal information
            analyst_data: Dictionary containing market analysis results
            
        Returns:
            Dictionary containing strategic recommendations and report
        """
        # Assess opportunity potential
        opportunity_assessment = self._assess_opportunity(crawler_data, analyst_data)
        
        # Generate strategic recommendations
        recommendations = self._generate_recommendations(opportunity_assessment)
        
        # Generate HTML report
        report_html = self._generate_report(crawler_data, analyst_data, recommendations)
        
        return {
            'success': True,
            'data': report_html
        }

    def _assess_opportunity(self, crawler_data: Dict[str, Any], analyst_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the overall opportunity potential."""
        # Calculate opportunity score
        score = 0
        factors = []
        
        # Market size factor
        market_size = float(analyst_data.get('market_size', '$0B').replace('$', '').replace('B', ''))
        if market_size > 100:
            score += 3
            factors.append('Large market opportunity')
        elif market_size > 50:
            score += 2
            factors.append('Moderate market opportunity')
        else:
            score += 1
            factors.append('Niche market opportunity')
        
        # Growth rate factor
        growth_rate = float(analyst_data.get('growth_rate', '0%').replace('%', '').replace(' CAGR', ''))
        if growth_rate > 10:
            score += 3
            factors.append('High growth potential')
        elif growth_rate > 5:
            score += 2
            factors.append('Moderate growth potential')
        else:
            score += 1
            factors.append('Stable market')
        
        # Pipeline strength factor
        pipeline_count = len(crawler_data.get('pipeline_info', []))
        if pipeline_count > 5:
            score += 3
            factors.append('Strong pipeline')
        elif pipeline_count > 2:
            score += 2
            factors.append('Moderate pipeline')
        else:
            score += 1
            factors.append('Limited pipeline')
        
        # Competitive position factor
        competitors = len(analyst_data.get('competitors', []))
        if competitors < 3:
            score += 3
            factors.append('Limited competition')
        elif competitors < 5:
            score += 2
            factors.append('Moderate competition')
        else:
            score += 1
            factors.append('High competition')
        
        # Determine opportunity category
        if score >= 10:
            category = 'high_potential'
        elif score >= 7:
            category = 'moderate_potential'
        else:
            category = 'high_risk'
        
        return {
            'score': score,
            'category': category,
            'factors': factors
        }

    def _generate_recommendations(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategic recommendations based on opportunity assessment."""
        category = assessment['category']
        template = self.recommendation_templates[category]
        
        recommendations = {
            'immediate_actions': [],
            'market_entry': [],
            'risk_mitigation': [],
            'value_creation': []
        }
        
        # Select recommendations based on category and factors
        for factor in assessment['factors']:
            if 'Large market' in factor or 'High growth' in factor:
                recommendations['immediate_actions'].append(self.strategic_frameworks['immediate_actions'][0])
                recommendations['market_entry'].append(self.strategic_frameworks['market_entry'][0])
            elif 'Strong pipeline' in factor:
                recommendations['immediate_actions'].append(self.strategic_frameworks['immediate_actions'][1])
                recommendations['value_creation'].append(self.strategic_frameworks['value_creation'][2])
            elif 'Limited competition' in factor:
                recommendations['market_entry'].append(self.strategic_frameworks['market_entry'][2])
                recommendations['value_creation'].append(self.strategic_frameworks['value_creation'][0])
            elif 'High competition' in factor:
                recommendations['risk_mitigation'].append(self.strategic_frameworks['risk_mitigation'][0])
                recommendations['risk_mitigation'].append(self.strategic_frameworks['risk_mitigation'][1])
        
        # Ensure at least one recommendation per category
        for category in recommendations:
            if not recommendations[category]:
                recommendations[category].append(self.strategic_frameworks[category][0])
        
        return recommendations

    def _generate_report(self, crawler_data: Dict[str, Any], analyst_data: Dict[str, Any], recommendations: Dict[str, Any]) -> str:
        """Generate HTML report with strategic recommendations."""
        company_name = crawler_data.get('company_name', 'Target Company')
        
        # Extract pipeline info
        pipeline_items = []
        if 'pipeline_info' in crawler_data:
            pipeline_info = crawler_data['pipeline_info']
            if 'phases' in pipeline_info:
                for phase, products in pipeline_info['phases'].items():
                    for product in products:
                        if isinstance(product, dict):
                            pipeline_items.append(f"{product.get('name', '')} - {product.get('indication', '')} ({phase})")
        
        # Extract deal info
        deal_items = []
        if 'deal_info' in crawler_data:
            deal_info = crawler_data['deal_info']
            for deal_type in ['partnerships', 'licenses', 'acquisitions', 'investments']:
                if deal_type in deal_info:
                    for deal in deal_info[deal_type]:
                        if isinstance(deal, dict):
                            deal_items.append(f"{deal.get('partner', '')} - {deal.get('context', '')} ({deal_type})")
        
        # Extract competitor names
        competitor_names = []
        if 'competitors' in analyst_data:
            for comp in analyst_data['competitors']:
                if isinstance(comp, dict):
                    competitor_names.append(comp.get('name', ''))
                elif isinstance(comp, str):
                    competitor_names.append(comp)
        
        # Extract therapeutic areas
        therapeutic_areas = []
        if 'therapeutic_areas' in analyst_data:
            for area in analyst_data['therapeutic_areas']:
                if isinstance(area, dict):
                    therapeutic_areas.append(area.get('name', ''))
                elif isinstance(area, str):
                    therapeutic_areas.append(area)
        
        # Extract mechanisms of action
        mechanisms = []
        if 'mechanisms_of_action' in analyst_data:
            for moa in analyst_data['mechanisms_of_action']:
                if isinstance(moa, dict):
                    mechanisms.append(moa.get('name', ''))
                elif isinstance(moa, str):
                    mechanisms.append(moa)
        
        # Extract trends
        trends = []
        if 'key_trends' in analyst_data:
            for trend in analyst_data['key_trends']:
                if isinstance(trend, dict):
                    trends.append(trend.get('description', ''))
                elif isinstance(trend, str):
                    trends.append(trend)
        
        # Extract risk factors
        risks = []
        if 'risk_factors' in analyst_data:
            for risk in analyst_data['risk_factors']:
                if isinstance(risk, dict):
                    risks.append(risk.get('description', ''))
                elif isinstance(risk, str):
                    risks.append(risk)
        
        html_report = f"""
        <div style="font-family: Inter, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: white;">
            <div style="text-align: center; margin-bottom: 30px; border-bottom: 3px solid #667eea; padding-bottom: 20px;">
                <h1 style="color: #2d3748; margin: 0; font-size: 2.5rem;">Market Pulse Analysis</h1>
                <h2 style="color: #667eea; margin: 10px 0; font-size: 2rem;">{company_name}</h2>
                <p style="color: #718096; font-size: 14px;">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
            
            <div style="margin-bottom: 25px; padding: 20px; background: linear-gradient(135deg, #f7fafc, #edf2f7); border-radius: 10px;">
                <h3 style="color: #2d3748; margin-top: 0; display: flex; align-items: center;">
                    <i class="fas fa-bullseye" style="margin-right: 10px; color: #667eea;"></i> Executive Summary
                </h3>
                <p style="line-height: 1.6; color: #4a5568; font-size: 16px;">
                    <strong>{company_name}</strong> presents a <strong style="color: #38a169;">high-potential opportunity</strong> 
                    in the life sciences sector with a diversified pipeline spanning multiple therapeutic areas. 
                    The company's strategic positioning in {', '.join(therapeutic_areas[:2])} markets 
                    offers significant growth potential with an estimated addressable market of 
                    <strong style="color: #667eea;">{analyst_data.get('market_size', 'N/A')}</strong> growing at 
                    <strong style="color: #38a169;">{analyst_data.get('growth_rate', 'N/A')}</strong>.
                </p>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
                <div style="padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 4px solid #667eea;">
                    <h4 style="color: #667eea; margin-top: 0; display: flex; align-items: center;">
                        <i class="fas fa-pills" style="margin-right: 8px;"></i> Pipeline Overview
                    </h4>
                    <ul style="color: #4a5568; line-height: 1.6; padding-left: 20px;">
                        {''.join([f'<li style="margin-bottom: 8px;">{item}</li>' for item in pipeline_items])}
                    </ul>
                </div>
                
                <div style="padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 4px solid #38a169;">
                    <h4 style="color: #38a169; margin-top: 0; display: flex; align-items: center;">
                        <i class="fas fa-handshake" style="margin-right: 8px;"></i> Recent Activity
                    </h4>
                    <ul style="color: #4a5568; line-height: 1.6; padding-left: 20px;">
                        {''.join([f'<li style="margin-bottom: 8px;">{item}</li>' for item in deal_items])}
                    </ul>
                </div>
            </div>
            
            <div style="margin-bottom: 25px; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h4 style="color: #667eea; margin-top: 0; display: flex; align-items: center;">
                    <i class="fas fa-crosshairs" style="margin-right: 8px;"></i> Therapeutic Focus Areas
                </h4>
                <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px;">
                    {''.join([f'<span style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: 500;">{area}</span>' for area in therapeutic_areas])}
                </div>
                <h5 style="color: #2d3748; margin: 15px 0 10px 0;">Mechanisms of Action:</h5>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                    {''.join([f'<span style="background: #f7fafc; color: #4a5568; padding: 6px 12px; border-radius: 15px; font-size: 13px; border: 1px solid #e2e8f0;">{moa}</span>' for moa in mechanisms])}
                </div>
            </div>
            
            <div style="margin-bottom: 25px; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h4 style="color: #667eea; margin-top: 0; display: flex; align-items: center;">
                    <i class="fas fa-users" style="margin-right: 8px;"></i> Competitive Landscape
                </h4>
                <div style="margin-bottom: 15px;">
                    <p style="color: #4a5568; line-height: 1.6; margin-bottom: 10px;">
                        <strong>Key Competitors:</strong> {', '.join(competitor_names)}
                    </p>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
                        <div style="background: #f0fff4; padding: 15px; border-radius: 8px; border-left: 3px solid #38a169;">
                            <strong style="color: #2d3748;">Market Size:</strong><br>
                            <span style="color: #38a169; font-size: 1.2em; font-weight: 600;">{analyst_data.get('market_size', 'N/A')}</span>
                        </div>
                        <div style="background: #f0f9ff; padding: 15px; border-radius: 8px; border-left: 3px solid #3182ce;">
                            <strong style="color: #2d3748;">Growth Rate:</strong><br>
                            <span style="color: #3182ce; font-size: 1.2em; font-weight: 600;">{analyst_data.get('growth_rate', 'N/A')}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom: 25px; padding: 20px; background: linear-gradient(135deg, #f0fff4, #c6f6d5); border-radius: 10px; border-left: 5px solid #38a169;">
                <h4 style="color: #2d3748; margin-top: 0; display: flex; align-items: center;">
                    <i class="fas fa-lightbulb" style="margin-right: 8px; color: #f6ad55;"></i> Strategic Recommendations
                </h4>
                <div style="display: grid; gap: 15px;">
                    <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <strong style="color: #2d3748;">🎯 Immediate Action:</strong>
                        <p style="margin: 5px 0 0 0; color: #4a5568;">{recommendations.get('immediate_actions', [''])[0]}</p>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <strong style="color: #2d3748;">🚀 Market Entry:</strong>
                        <p style="margin: 5px 0 0 0; color: #4a5568;">{recommendations.get('market_entry', [''])[0]}</p>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <strong style="color: #2d3748;">⚠️ Risk Mitigation:</strong>
                        <p style="margin: 5px 0 0 0; color: #4a5568;">{recommendations.get('risk_mitigation', [''])[0]}</p>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <strong style="color: #2d3748;">💎 Value Creation:</strong>
                        <p style="margin: 5px 0 0 0; color: #4a5568;">{recommendations.get('value_creation', [''])[0]}</p>
                    </div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
                <div style="padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h4 style="color: #667eea; margin-top: 0; display: flex; align-items: center;">
                        <i class="fas fa-chart-line" style="margin-right: 8px;"></i> Market Trends
                    </h4>
                    <ul style="color: #4a5568; line-height: 1.6; padding-left: 20px;">
                        {''.join([f'<li style="margin-bottom: 8px;">{trend}</li>' for trend in trends])}
                    </ul>
                </div>
                
                <div style="padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h4 style="color: #e53e3e; margin-top: 0; display: flex; align-items: center;">
                        <i class="fas fa-exclamation-triangle" style="margin-right: 8px;"></i> Risk Factors
                    </h4>
                    <ul style="color: #4a5568; line-height: 1.6; padding-left: 20px;">
                        {''.join([f'<li style="margin-bottom: 8px;">{risk}</li>' for risk in risks])}
                    </ul>
                </div>
            </div>
            
            <div style="text-align: center; padding: 20px; background: #f7fafc; border-radius: 10px; margin-top: 30px;">
                <p style="color: #718096; font-size: 12px; margin: 0;">
                    This report was generated by Market Pulse AI • Confidential & Proprietary<br>
                    For questions or additional analysis, contact your BD team
                </p>
            </div>
        </div>
        """
        
        return html_report

    def _get_hermes_response(self, prompt: str) -> str:
        """Get response from OpenHermes model using Ollama."""
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
            return "Error in OpenHermes analysis" 