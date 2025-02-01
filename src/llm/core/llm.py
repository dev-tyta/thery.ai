from typing import Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage
import logging
from src.llm.core.config import settings
from src.llm.utils.logging import TheryBotLogger

class LLMError(Exception):
    """Custom exception for LLM-related errors"""
    pass

class TheryLLM:
    """Enhanced LLM wrapper with safety checks and response validation"""
    
    def __init__(
        self,
        model_name: str = "gemini-1.5-flash",
        temperature: float = 0.7,
        max_retries: int = 3,
        safety_threshold: float = 0.95,
        logger: Optional[TheryBotLogger] = None
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_retries = max_retries
        self.safety_threshold = safety_threshold
        self.logger = logger or TheryBotLogger()
        self._initialize_llm()
    
    def _initialize_llm(self) -> None:
        """Initialize the LLM with proper error handling"""
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=self.temperature,
                max_retries=self.max_retries,
                google_api_key=settings.GOOGLE_API_KEY
            )
            self._session_active = True
        except Exception as e:
            self._session_active = False
            self.logger.log_interaction(
                interaction_type="llm_initialization_failed",
                data={"error": str(e)},
                level=logging.ERROR
            )
            raise LLMError(f"LLM initialization failed: {str(e)}")
    
    def generate(self, prompt: str, **kwargs) -> AIMessage:
        """Generate a response with safety checks and validation"""
        if not self._session_active:
            self._initialize_llm()
        
        try:
            # Log the generation attempt
            self.logger.log_interaction(
                interaction_type="llm_generation_attempt",
                data={"prompt": prompt, "kwargs": kwargs},
                level=logging.INFO
            )
            
            # Generate response
            response = self.llm.invoke(prompt)
            
            # Validate response
            validated_response = self._validate_response(response)
            
            # Log successful generation
            self.logger.log_interaction(
                interaction_type="llm_generation_success",
                data={"prompt": prompt, "response": str(validated_response)},
                level=logging.INFO
            )
            
            return validated_response
            
        except Exception as e:
            self.logger.log_interaction(
                interaction_type="llm_generation_error",
                data={"prompt": prompt, "error": str(e)},
                level=logging.ERROR
            )
            raise LLMError(f"Generation failed: {str(e)}")
    
    def _validate_response(
        self,
        response: AIMessage
    ) -> AIMessage:
        """Validate response content and format"""
        if not isinstance(response, AIMessage):
            self.logger.log_interaction(
                interaction_type="llm_invalid_response_type",
                data={"response": response},
                level=logging.ERROR
            )
            raise LLMError("Invalid response type")
            
        if not response.content.strip():
            self.logger.log_interaction(
                interaction_type="llm_empty_response",
                data={"response": response},
                level=logging.ERROR
            )
            raise LLMError("Empty response content")
            
        return response