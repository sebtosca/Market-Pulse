import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import base64
import io
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor

# Import real agents
from src.agents.crawler import CrawlerAgent
from src.agents.analyst import AnalystAgent
from src.agents.advisor import AdvisorAgent

# Initialize agents
crawler_agent = CrawlerAgent()
analyst_agent = AnalystAgent()
advisor_agent = AdvisorAgent()

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Custom CSS styling for the app
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Inter', sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .main-container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                text-align: center;
                color: white;
                margin-bottom: 30px;
            }
            .header h1 {
                font-size: 3rem;
                font-weight: 700;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .header p {
                font-size: 1.2rem;
                opacity: 0.9;
                margin-top: 10px;
            }
            .input-card {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            .results-card {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            .agent-status {
                display: flex;
                justify-content: space-around;
                margin: 20px 0;
                flex-wrap: wrap;
                gap: 10px;
            }
            .agent-step {
                text-align: center;
                padding: 15px;
                border-radius: 10px;
                min-width: 150px;
                transition: all 0.3s ease;
                flex: 1;
                max-width: 200px;
            }
            .agent-step.active {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
            }
            .agent-step.completed {
                background: linear-gradient(135deg, #56ab2f, #a8e6cf);
                color: white;
            }
            .agent-step.pending {
                background: #f8f9fa;
                color: #6c757d;
                border: 2px dashed #dee2e6;
            }
            .agent-step.error {
                background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                color: white;
            }
            .report-content {
                border: 1px solid #e9ecef;
                border-radius: 10px;
                padding: 20px;
                background: #f8f9fa;
                max-height: 600px;
                overflow-y: auto;
            }
            .loading-spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 10px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .error-message {
                background: #fed7d7;
                color: #c53030;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
                border-left: 4px solid #e53e3e;
            }
            .success-message {
                background: #c6f6d5;
                color: #2d3748;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
                border-left: 4px solid #38a169;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Global variables to store analysis state
analysis_state = {
    'is_running': False,
    'current_agent': 0,
    'agents_status': ['pending', 'pending', 'pending'],
    'error_message': None,
    'report_html': None,
    'start_time': None,
    'agent_times': {
        'crawler': 0,
        'analyst': 0,
        'advisor': 0
    }
}

# App layout (copied from the mock code)
app.layout = html.Div([
    dcc.Store(id='analysis-store', data=analysis_state),
    dcc.Interval(id='progress-interval', interval=1000, disabled=True),
    html.Div([
        # Header
        html.Div([
            html.H1([
                html.I(className="fas fa-chart-line", style={'marginRight': '15px'}),
                "Market Pulse AI"
            ]),
            html.P("Multi-Agent Business Intelligence")
        ], className="header"),
        # Input Card
        html.Div([
            html.H2([
                html.I(className="fas fa-search", style={'marginRight': '10px'}),
                "Analysis Input"
            ], style={'marginBottom': '20px', 'color': '#2d3748'}),
            html.Div([
                html.Label("Input Type:", style={'fontWeight': '600', 'marginBottom': '8px', 'display': 'block'}),
                dcc.RadioItems(
                    id='input-type',
                    options=[
                        {'label': ' Press Release URL', 'value': 'url'},
                        {'label': ' Company Name', 'value': 'company'}
                    ],
                    value='url',
                    inline=True,
                    style={'marginBottom': '20px'}
                )
            ]),
            html.Div([
                html.Label(id='input-label', children="Company Name:", 
                          style={'fontWeight': '600', 'marginBottom': '8px', 'display': 'block'}),
                dcc.Input(
                    id='input-field',
                    type='text',
                    placeholder='Enter company name (e.g., Pfizer, Moderna, Roche)',
                    style={
                        'width': '100%',
                        'padding': '12px',
                        'border': '2px solid #e2e8f0',
                        'borderRadius': '8px',
                        'fontSize': '16px',
                        'marginBottom': '20px'
                    }
                )
            ]),
            html.Div(id='error-display'),
            html.Button([
                html.I(className="fas fa-rocket", style={'marginRight': '8px'}),
                "Launch Analysis"
            ], 
            id='analyze-btn', 
            n_clicks=0,
            style={
                'background': 'linear-gradient(135deg, #667eea, #764ba2)',
                'color': 'white',
                'border': 'none',
                'padding': '15px 30px',
                'borderRadius': '25px',
                'fontSize': '16px',
                'fontWeight': '600',
                'cursor': 'pointer',
                'width': '200px'
            })
        ], className="input-card"),
        # Agent Status Tracker
        html.Div([
            html.H3([
                html.I(className="fas fa-users", style={'marginRight': '10px'}),
                "Agent Pipeline Status"
            ], style={'textAlign': 'center', 'marginBottom': '30px', 'color': '#2d3748'}),
            html.Div([
                html.Div([
                    html.I(className="fas fa-spider", style={'fontSize': '24px', 'marginBottom': '10px'}),
                    html.H4("Crawler", style={'margin': '0', 'fontSize': '16px'}),
                    html.P("Data Extraction", style={'margin': '5px 0 0 0', 'fontSize': '12px'}),
                    html.Div(id='agent-1-progress', style={'marginTop': '10px'})
                ], id='agent-1-status', className="agent-step pending"),
                html.Div([
                    html.I(className="fas fa-brain", style={'fontSize': '24px', 'marginBottom': '10px'}),
                    html.H4("Analyst", style={'margin': '0', 'fontSize': '16px'}),
                    html.P("Market Analysis", style={'margin': '5px 0 0 0', 'fontSize': '12px'}),
                    html.Div(id='agent-2-progress', style={'marginTop': '10px'})
                ], id='agent-2-status', className="agent-step pending"),
                html.Div([
                    html.I(className="fas fa-chart-pie", style={'fontSize': '24px', 'marginBottom': '10px'}),
                    html.H4("Advisor", style={'margin': '0', 'fontSize': '16px'}),
                    html.P("Strategic Report", style={'margin': '5px 0 0 0', 'fontSize': '12px'}),
                    html.Div(id='agent-3-progress', style={'marginTop': '10px'})
                ], id='agent-3-status', className="agent-step pending")
            ], className="agent-status")
        ], className="results-card", id='status-card', style={'display': 'none'}),
        # Results Card
        html.Div([
            html.H3([
                html.I(className="fas fa-file-alt", style={'marginRight': '10px'}),
                "Market Analysis Report"
            ], style={'marginBottom': '20px', 'color': '#2d3748'}),
            html.Div(id='report-content', className="report-content"),
            html.Div(id='report-data', style={'display': 'none'})
        ], className="results-card", id='results-card', style={'display': 'none'}),
    ], className="main-container")
])

# Agent functions
def agent_1_crawler(input_value, input_type):
    try:
        print(f"\nProcessing input: {input_value} (type: {input_type})")
        
        # Process input using crawler agent
        result = crawler_agent.process(input_value)
        
        if "error" in result:
            print(f"Crawler error: {result['error']}")
            return {'success': False, 'error': result['error']}
        
        if not result:
            print("Crawler returned empty result")
            return {'success': False, 'error': 'No data found'}
        
        print("Crawler result structure:", result.keys())
        
        # Ensure we have the minimum required data
        if not result.get('pipeline_info') and not result.get('deal_info'):
            print("No pipeline or deal info found")
            return {'success': False, 'error': 'No pipeline or deal information found'}
        
        # Structure the data for the analyst
        structured_data = {
            'success': True,
            'pipeline_info': {
                'phases': {},
                'indications': {}
            },
            'deal_info': {
                'partnerships': [],
                'licenses': [],
                'acquisitions': [],
                'investments': []
            },
            'entities': {},
            'raw_text': result.get('raw_text', ''),
            'source_url': result.get('source_url', ''),
            'market_cap': result.get('market_cap', 'N/A'),
            'revenue': result.get('revenue', 'N/A'),
            'rd_spend': result.get('rd_spend', 'N/A'),
            'pipeline_stage': result.get('pipeline_stage', 'N/A'),
            'therapeutic_areas': result.get('therapeutic_areas', []),
            'mechanisms': result.get('mechanisms', [])
        }
        
        # Process pipeline info
        if result.get('pipeline_info'):
            pipeline_data = result['pipeline_info']
            if isinstance(pipeline_data, dict):
                # Handle dictionary format
                if 'phases' in pipeline_data:
                    structured_data['pipeline_info']['phases'] = pipeline_data['phases']
                if 'indications' in pipeline_data:
                    structured_data['pipeline_info']['indications'] = pipeline_data['indications']
            elif isinstance(pipeline_data, list):
                # Convert list to dictionary format
                for item in pipeline_data:
                    phase = item.get('phase', 'Unknown')
                    if phase not in structured_data['pipeline_info']['phases']:
                        structured_data['pipeline_info']['phases'][phase] = []
                    structured_data['pipeline_info']['phases'][phase].append({
                        'name': item.get('drug', ''),
                        'indication': item.get('indication', ''),
                        'context': item.get('context', '')
                    })
        
        # Process deal info
        if result.get('deal_info'):
            deal_data = result['deal_info']
            if isinstance(deal_data, dict):
                # Handle dictionary format
                for deal_type in ['partnerships', 'licenses', 'acquisitions', 'investments']:
                    if deal_type in deal_data:
                        structured_data['deal_info'][deal_type] = deal_data[deal_type]
            elif isinstance(deal_data, list):
                # Convert list to dictionary format
                for deal in deal_data:
                    deal_type = deal.get('type', 'partnerships')
                    if deal_type not in structured_data['deal_info']:
                        structured_data['deal_info'][deal_type] = []
                    structured_data['deal_info'][deal_type].append({
                        'partner': deal.get('partner', ''),
                        'context': deal.get('context', '')
                    })
        
        # Process entities
        if result.get('entities'):
            entities = result['entities']
            if isinstance(entities, dict):
                structured_data['entities'] = entities
            elif isinstance(entities, list):
                # Convert list to dictionary format
                entity_dict = {}
                for entity in entities:
                    entity_type = entity.get('type', 'ORG')
                    if entity_type not in entity_dict:
                        entity_dict[entity_type] = []
                    entity_dict[entity_type].append(entity.get('text', ''))
                structured_data['entities'] = entity_dict
        
        print("Structured data keys:", structured_data.keys())
        return structured_data
        
    except Exception as e:
        print(f"Error in crawler agent: {str(e)}")
        return {'success': False, 'error': str(e)}

def agent_2_analyst(crawler_data):
    try:
        if not crawler_data.get('success'):
            return {'success': False, 'error': crawler_data.get('error', 'Invalid crawler data')}
        
        # Ensure we have the required data structure
        if not isinstance(crawler_data, dict):
            return {'success': False, 'error': 'Invalid data format from crawler'}
        
        # Process the data using analyst agent
        result = analyst_agent.process(crawler_data)
        
        if "error" in result:
            return {'success': False, 'error': result['error']}
        
        return {
            'success': True,
            'therapeutic_areas': result.get('therapeutic_areas', []),
            'mechanisms_of_action': result.get('mechanisms_of_action', []),
            'competitors': result.get('competitors', []),
            'market_size': result.get('market_size', 'N/A'),
            'growth_rate': result.get('growth_rate', 'N/A'),
            'key_trends': result.get('key_trends', []),
            'risk_factors': result.get('risk_factors', [])
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def agent_3_advisor(crawler_data, analyst_data):
    try:
        if not crawler_data.get('success') or not analyst_data.get('success'):
            return {'success': False, 'error': 'Invalid input data'}
        
        # Ensure we have the required data structure
        if not isinstance(crawler_data, dict) or not isinstance(analyst_data, dict):
            return {'success': False, 'error': 'Invalid data format from previous agents'}
        
        # Process using advisor agent with separate arguments
        result = advisor_agent.process(crawler_data, analyst_data)
        
        if "error" in result:
            return {'success': False, 'error': result['error']}
        
        return {
            'success': True,
            'html': result.get('data', '')  # Note: changed from 'html' to 'data' to match advisor output
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Callback to update input label based on type
@app.callback(
    [Output('input-label', 'children'),
     Output('input-field', 'placeholder')],
    [Input('input-type', 'value')]
)
def update_input_label(input_type):
    if input_type == 'company':
        return "Company Name:", "Enter company name (e.g., Pfizer, Moderna, Roche)"
    else:
        return "Press Release URL:", "Enter press release URL (e.g., https://...)"

# Callback to start analysis
@app.callback(
    [Output('analysis-store', 'data'),
     Output('progress-interval', 'disabled'),
     Output('status-card', 'style'),
     Output('error-display', 'children')],
    [Input('analyze-btn', 'n_clicks')],
    [State('input-field', 'value'),
     State('input-type', 'value'),
     State('analysis-store', 'data')]
)
def start_analysis(n_clicks, input_value, input_type, current_state):
    if n_clicks == 0 or not input_value or not input_value.strip():
        return current_state, True, {'display': 'none'}, ""
    
    if current_state.get('is_running'):
        return current_state, False, {'display': 'block'}, ""
    
    # Preserve the previous report if it exists
    previous_report = current_state.get('report_html') if current_state else None
    
    # Reset state but keep the previous report
    new_state = {
        'is_running': True,
        'current_agent': 1,
        'agents_status': ['active', 'pending', 'pending'],
        'error_message': None,
        'report_html': previous_report,  # Keep the previous report
        'input_value': input_value.strip(),
        'input_type': input_type,
        'start_time': time.time()
    }
    
    return new_state, False, {'display': 'block'}, ""

# Callback to update progress
@app.callback(
    [Output('analysis-store', 'data', allow_duplicate=True),
     Output('agent-1-status', 'className'),
     Output('agent-2-status', 'className'),
     Output('agent-3-status', 'className'),
     Output('agent-1-progress', 'children'),
     Output('agent-2-progress', 'children'),
     Output('agent-3-progress', 'children'),
     Output('results-card', 'style'),
     Output('report-content', 'children'),
     Output('report-data', 'children')],
    [Input('progress-interval', 'n_intervals')],
    [State('analysis-store', 'data')],
    prevent_initial_call=True
)
def update_progress(n_intervals, state):
    if not state.get('is_running'):
        # If not running and we have a report, show completed status
        if state.get('report_html'):
            report_content = html.Iframe(
                srcDoc=state['report_html'],
                style={'width': '100%', 'height': '600px', 'border': 'none', 'borderRadius': '8px'}
            )
            return (
                state,
                'agent-step completed',
                'agent-step completed',
                'agent-step completed',
                html.Div("✓ Complete", style={'fontSize': '12px', 'color': 'white'}),
                html.Div("✓ Complete", style={'fontSize': '12px', 'color': 'white'}),
                html.Div("✓ Complete", style={'fontSize': '12px', 'color': 'white'}),
                {'display': 'block'},
                report_content,
                state['report_html']
            )
        return state, 'agent-step pending', 'agent-step pending', 'agent-step pending', "", "", "", {'display': 'none'}, "", ""
    
    current_time = time.time()
    start_time = state.get('start_time', current_time)
    elapsed = current_time - start_time
    
    # Agent 1: Crawler
    if state['current_agent'] == 1:
        agent_1_class = 'agent-step active'
        agent_2_class = 'agent-step pending'
        agent_3_class = 'agent-step pending'
        agent_1_progress = html.Div([
            html.Div(className="loading-spinner", style={'display': 'inline-block'}),
            "Extracting data..."
        ], style={'fontSize': '12px'})
        agent_2_progress = ""
        agent_3_progress = ""
        
        # Run Agent 1
        crawler_data = agent_1_crawler(state['input_value'], state['input_type'])
        if crawler_data['success']:
            state['crawler_data'] = crawler_data
            state['current_agent'] = 2
        else:
            state['error_message'] = crawler_data.get('error', 'Unknown error')
            state['is_running'] = False
            return state, 'agent-step error', agent_2_class, agent_3_class, "Error", agent_2_progress, agent_3_progress, {'display': 'none'}, "", ""
        
        return state, agent_1_class, agent_2_class, agent_3_class, agent_1_progress, agent_2_progress, agent_3_progress, {'display': 'none'}, "", ""
    
    # Agent 2: Analyst
    elif state['current_agent'] == 2:
        agent_1_class = 'agent-step completed'
        agent_2_class = 'agent-step active'
        agent_3_class = 'agent-step pending'
        agent_1_progress = html.Div("✓ Complete", style={'fontSize': '12px', 'color': 'white'})
        agent_2_progress = html.Div([
            html.Div(className="loading-spinner", style={'display': 'inline-block'}),
            "Analyzing market..."
        ], style={'fontSize': '12px'})
        agent_3_progress = ""
        
        # Run Agent 2
        analyst_data = agent_2_analyst(state.get('crawler_data', {}))
        if analyst_data['success']:
            state['analyst_data'] = analyst_data
            state['current_agent'] = 3
        else:
            state['error_message'] = analyst_data.get('error', 'Unknown error')
            state['is_running'] = False
            return state, agent_1_class, 'agent-step error', agent_3_class, agent_1_progress, "Error", agent_3_progress, {'display': 'none'}, "", ""
        
        return state, agent_1_class, agent_2_class, agent_3_class, agent_1_progress, agent_2_progress, agent_3_progress, {'display': 'none'}, "", ""
    
    # Agent 3: Advisor
    elif state['current_agent'] == 3:
        agent_1_class = 'agent-step completed'
        agent_2_class = 'agent-step completed'
        agent_3_class = 'agent-step active'
        agent_1_progress = html.Div("✓ Complete", style={'fontSize': '12px', 'color': 'white'})
        agent_2_progress = html.Div("✓ Complete", style={'fontSize': '12px', 'color': 'white'})
        agent_3_progress = html.Div([
            html.Div(className="loading-spinner", style={'display': 'inline-block'}),
            "Generating report..."
        ], style={'fontSize': '12px'})
        
        # Run Agent 3
        advisor_result = agent_3_advisor(state.get('crawler_data', {}), state.get('analyst_data', {}))
        if advisor_result['success']:
            state['report_html'] = advisor_result.get('html', '')
            state['is_running'] = False
            
            # All agents completed successfully
            agent_1_class = 'agent-step completed'
            agent_2_class = 'agent-step completed'
            agent_3_class = 'agent-step completed'
            agent_1_progress = html.Div("✓ Complete", style={'fontSize': '12px', 'color': 'white'})
            agent_2_progress = html.Div("✓ Complete", style={'fontSize': '12px', 'color': 'white'})
            agent_3_progress = html.Div("✓ Complete", style={'fontSize': '12px', 'color': 'white'})
            
            report_content = html.Iframe(
                srcDoc=state['report_html'],
                style={'width': '100%', 'height': '600px', 'border': 'none', 'borderRadius': '8px'}
            ) if state['report_html'] else ""
            
            return state, agent_1_class, agent_2_class, agent_3_class, agent_1_progress, agent_2_progress, agent_3_progress, {'display': 'block'}, report_content, state['report_html']
        else:
            state['error_message'] = advisor_result.get('error', 'Unknown error')
            state['is_running'] = False
            return state, agent_1_class, agent_2_class, 'agent-step error', agent_1_progress, agent_2_progress, "Error", {'display': 'none'}, "", ""
    
    # Default return
    return state, 'agent-step pending', 'agent-step pending', 'agent-step pending', "", "", "", {'display': 'none'}, "", ""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050)