from typing import Dict, Any
from .base_agent import BaseAgent
from src.llm.memory.vector_store import FAISSVectorSearch
from langchain_community.tools.tavily_search import TavilySearchResults

class ContextAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vector_search = FAISSVectorSearch()
        self.web_search = TavilySearchResults()
    
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
