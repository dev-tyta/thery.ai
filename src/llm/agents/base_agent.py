from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from src.llm.core.llm import TheryLLM
from src.llm.memory.history import History

class BaseAgent(ABC):
    def __init__(
        self,
        llm: Optional[TheryLLM] = None,
        history: Optional[History] = None
    ):
        self.llm = llm or TheryLLM()
        self.history = history or History()
    
    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        """Process the input and return response"""
        pass
    
    def _log_action(self, action: str, metadata: Dict[str, Any]) -> None:
        """Log agent actions"""
        # Implement logging logic here
        pass