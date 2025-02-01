import os
from typing import Dict, Any
from .base_agent import BaseAgent
from src.llm.core.config import settings
from src.llm.memory.vector_store import FAISSVectorSearch
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper

class ContextAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initialize_tools()

    def _initialize_tools(self) -> None:
        """Lazy-load expensive resources"""
        self.web_search = TavilySearchResults(
            max_results=settings.TAVILY_MAX_RESULTS,
            include_answer=settings.TAVILY_INCLUDE_ANSWER,
            include_images=settings.TAVILY_INCLUDE_IMAGES,  # Disabled until needed
            api_wrapper=TavilySearchAPIWrapper(tavily_api_key=settings.TAVILY_API_KEY)
        )
        
        self.vector_search = FAISSVectorSearch()

    def process(self, query: str) -> Dict[str, str]:
        """Gather context from multiple sources"""
        web_context = self._get_web_context(query)
        vector_context = self._get_vector_context(query)
        
        return {
            "web_context": web_context,
            "vector_context": vector_context,
            "combined_context": f"{web_context}\n\n{vector_context}"
        }
    
    def _get_web_context(self, query: str) -> str:
        try:
            results = self.web_search.invoke(query)
            return "\n".join([res["content"] for res in results])
        except Exception as e:
            self._log_action("web_search_error", {"error": str(e)})
            return "Web search unavailable"
    
    def _get_vector_context(self, query: str) -> str:
        try:
            return self.vector_search(query)
        except Exception as e:
            self._log_action("vector_search_error", {"error": str(e)})
            return "Vector search unavailable"
