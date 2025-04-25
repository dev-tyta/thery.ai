from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
import logging
from src.llm.core.llm import TheryLLM
from src.llm.utils.logging import TheryBotLogger
from src.llm.memory.history import RedisHistory
from src.llm.memory.session_manager import SessionManager

class BaseAgent(ABC):
    def __init__(
        self,
        llm: Optional[TheryLLM] = None,
        history: Optional[RedisHistory] = None,
        session_manager: Optional[SessionManager] = None
    ):
        self.llm = llm or TheryLLM()
        self.logger = TheryBotLogger()
        self.history = history or RedisHistory()
        self.memory_manager = session_manager or SessionManager()
    
    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        """Process the input and return response"""
        pass
        
    
    def _log_action(
        self,
        action: str,
        metadata: Dict[str, Any],
        level: str = logging.INFO,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        """
        Log agent actions with metadata and optional session/user context.
        
        Args:
            action: The action being logged (e.g., "llm_generation_attempt").
            metadata: A dictionary of metadata related to the action.
            level: The log level ("info", "warning", "error", etc.).
            session_id: Optional session ID for context.
            user_id: Optional user ID for context.
        """
        # Prepare log data
        log_data = {
            "action": action,
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Add session and user context if provided
        if session_id:
            log_data["session_id"] = session_id
        if user_id:
            log_data["user_id"] = user_id

        # Log the data using the existing logger
        if hasattr(self, "logger"):
            self.logger.log_interaction(
                interaction_type="agent_action",
                data=log_data,
                level=level
            )
        else:
            print(f"Logging failed: {log_data}")