from typing import Dict, Any
import autogen
from config.model_config import AUTOGEN_CONFIG, MODEL_CONFIGS

def create_crawler_agent() -> autogen.AssistantAgent:
    """Create the Crawler agent configuration."""
    return autogen.AssistantAgent(
        name="Crawler",
        llm_config=AUTOGEN_CONFIG["llm_config"],
        system_message="""You are a specialized web crawler agent for pharmaceutical and biotech information.
        Your tasks include:
        1. Extracting pipeline information from company websites and press releases
        2. Identifying deal information and partnerships
        3. Collecting relevant financial data
        4. Ensuring data accuracy and completeness
        
        Use the provided scraping tools to gather information efficiently and accurately."""
    )

def create_analyst_agent() -> autogen.AssistantAgent:
    """Create the Analyst agent configuration."""
    return autogen.AssistantAgent(
        name="Analyst",
        llm_config=AUTOGEN_CONFIG["llm_config"],
        system_message="""You are a pharmaceutical industry analyst specializing in:
        1. Identifying therapeutic areas and mechanisms of action
        2. Analyzing competitive landscapes
        3. Evaluating market opportunities
        4. Assessing scientific and commercial potential
        
        Use NER tools and your expertise to provide detailed analysis."""
    )

def create_advisor_agent() -> autogen.AssistantAgent:
    """Create the Advisor agent configuration."""
    return autogen.AssistantAgent(
        name="Advisor",
        llm_config=AUTOGEN_CONFIG["llm_config"],
        system_message="""You are a business development advisor specializing in:
        1. Creating concise opportunity memos
        2. Formatting reports for BD teams
        3. Highlighting key strategic insights
        4. Providing actionable recommendations
        
        Use your expertise to create clear, actionable reports."""
    )

def create_user_proxy() -> autogen.UserProxyAgent:
    """Create the User Proxy agent configuration."""
    return autogen.UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={"work_dir": "workspace"},
        llm_config=AUTOGEN_CONFIG["llm_config"],
        system_message="""You are a user proxy agent that coordinates the workflow between:
        1. The Crawler agent for data collection
        2. The Analyst agent for information processing
        3. The Advisor agent for report generation
        
        Your role is to ensure smooth communication and task completion."""
    )

def create_group_chat_config() -> Dict[str, Any]:
    """Create the group chat configuration."""
    return {
        "messages": [],
        "max_round": 50,
        "speaker_selection_method": "round_robin",
        "allow_repeat_speaker": False
    }

def initialize_agents() -> Dict[str, Any]:
    """Initialize all agents and return their configurations."""
    return {
        "crawler": create_crawler_agent(),
        "analyst": create_analyst_agent(),
        "advisor": create_advisor_agent(),
        "user_proxy": create_user_proxy(),
        "group_chat_config": create_group_chat_config()
    } 