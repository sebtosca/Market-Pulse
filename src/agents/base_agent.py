from abc import ABC, abstractmethod
from typing import Any, Dict
import logging
from pathlib import Path

class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the agent."""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        fh = logging.FileHandler(log_dir / f"{self.name}.log")
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    @abstractmethod
    def process(self, input_data: Any) -> Dict[str, Any]:
        """Process the input data and return results.
        
        Args:
            input_data: The input data to process
            
        Returns:
            Dict containing the processing results
        """
        pass
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate the input data.
        
        Args:
            input_data: The input data to validate
            
        Returns:
            bool indicating if the input is valid
        """
        return True
    
    def log_error(self, error: Exception) -> None:
        """Log an error with the agent's logger.
        
        Args:
            error: The exception to log
        """
        self.logger.error(f"Error in {self.name}: {str(error)}", exc_info=True) 