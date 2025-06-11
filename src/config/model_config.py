from typing import Dict, Any
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Model configurations
MODEL_CONFIGS = {
    "mistral": {
        "name": "mistral-7b-instruct",
        "provider": "ollama",
        "parameters": {
            "temperature": 0.7,
            "top_p": 0.95,
            "max_tokens": 2000,
            "context_window": 4096
        }
    },
    "llama": {
        "name": "llama2-8b-instruct",
        "provider": "ollama",
        "parameters": {
            "temperature": 0.7,
            "top_p": 0.95,
            "max_tokens": 2000,
            "context_window": 4096
        }
    }
}

# NER Model configurations
NER_CONFIGS = {
    "scispacy": {
        "model": "en_core_sci_sm",
        "threshold": 0.5
    },
    "biobert": {
        "model": "biobert-base-cased-v1.2",
        "threshold": 0.5
    }
}

# AutoGen configurations
AUTOGEN_CONFIG = {
    "llm_config": {
        "config_list": [
            {
                "model": MODEL_CONFIGS["mistral"]["name"],
                "api_base": "http://localhost:11434/v1",
                "api_type": "open_ai",
                "api_key": "not-needed"
            }
        ],
        "temperature": 0.7
    },
    "timeout": 600,
    "cache_seed": 42
}

# Tool configurations
TOOL_CONFIGS = {
    "scraper": {
        "timeout": 30,
        "max_retries": 3,
        "user_agent": "MarketPulse/1.0 (Business Development Analysis Tool)"
    },
    "ner": {
        "batch_size": 32,
        "max_length": 512
    },
    "formatter": {
        "template_path": "src/templates",
        "output_formats": ["json", "pdf", "html"],
        "default_format": "pdf",
        "styles": {
            "primary_color": "#2c3e50",
            "secondary_color": "#e8f4f8",
            "accent_color": "#3498db",
            "font_family": "Arial, sans-serif",
            "font_size": "14px",
            "line_height": "1.6"
        }
    }
}

# Path configurations
PATHS = {
    "models": Path(__file__).parent.parent.parent / "models",
    "data": Path(__file__).parent.parent.parent / "data",
    "reports": Path(__file__).parent.parent.parent / "reports",
    "logs": Path(__file__).parent.parent.parent / "logs",
    "templates": Path(__file__).parent.parent / "templates"
}

# Create necessary directories
for path in PATHS.values():
    path.mkdir(parents=True, exist_ok=True)

# Environment variables
ENV_VARS = {
    "OLLAMA_HOST": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
    "MODEL_PROVIDER": os.getenv("MODEL_PROVIDER", "ollama"),
    "DEFAULT_MODEL": os.getenv("DEFAULT_MODEL", "mistral"),
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO")
} 