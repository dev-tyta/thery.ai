import os
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List, Annotated, Dict, Tuple
from logging import getLogger
from pathlib import Path
from src.llm.core import TheTherapistLLM
from src.memory.history import History
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from src.llm.core import FAISSVectorSearch
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

# For TensorFlow-related warnings (if any)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

logger = getLogger(__name__)


class ConversationResponse(BaseModel):
    """Structured response container with full context"""
    response: str = Field(..., description="Primary assistant response")
    context: str = Field(..., description="Combined context sources")
    web_context: str = Field(..., description="Web search results")
    vector_db_context: str = Field(..., description="Vector DB matches")
    query: str = Field(..., description="Original user query")


class LLMConversation:
    """Main conversation orchestrator with state management"""
    
    def __init__(
        self,
        llm: Optional['TheTherapistLLM'] = None,
        history: Optional['History'] = None,
        vector_db_path: Path = Path("vector_embedding/mental_health_vector_db")
    ):
        self.llm = llm or TheTherapistLLM()
        self.history = history or History()
        self.vector_db_path = vector_db_path
        self._initialize_tools()

    def _initialize_tools(self) -> None:
        """Lazy-load expensive resources"""
        self.tavily_tool = TavilySearchResults(
            max_results=3,
            include_answer=True,
            include_images=False,  # Disabled until needed
            api_wrapper=TavilySearchAPIWrapper(tavily_api_key=os.getenv("TAVILY_API_KEY"))
        )
        
        self.vector_search = FAISSVectorSearch(
            embedding_model=HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={
                    "padding": "max_length",
                    "max_length": 512,
                    "truncation": True,
                    "normalize_embeddings": True
                }
            ),
            db_path=self.vector_db_path
        )

    def process_query(
        self,
        query: str,
        chat_history: Optional[List[Dict]] = None
    ) -> ConversationResponse:
        """Main entry point for conversation processing"""
        try:
            web_context = self._web_search(query)
            vector_context = self._vector_search(query)

            return self._build_response(
                query=query,
                web_context=web_context,
                vector_context=vector_context
            )
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            return self._fallback_response(query)

    def _web_search(self, query: str) -> str:
        """Web search with error isolation"""
        try:
            results = self.tavily_tool.invoke(query)
            return "\n".join([res["content"] for res in results])
        except Exception as e:
            logger.warning(f"Web search failed: {str(e)}")
            return "No web results available"

    def _vector_search(self, query: str) -> str:
        """Vector DB search with error isolation"""
        try:
            return self.vector_search(query)
        except Exception as e:
            logger.warning(f"Vector search failed: {str(e)}")
            return "No vector matches found"

    def _build_response(
        self,
        query: str,
        web_context: str,
        vector_context: str
    ) -> ConversationResponse:
        """Construct validated response object"""
        combined_context = (
            f"Vector DB Context:\n{vector_context}\n\nWeb Context:\n{web_context}"
        )
        
        prompt = self._construct_prompt(query, combined_context)
        llm_response = self.llm.generate(prompt)
        llm_response = llm_response.content.strip()
        
        return ConversationResponse(
            response=llm_response,
            context=combined_context,
            web_context=web_context,
            vector_db_context=vector_context,
            query=query
        )

    @staticmethod
    def _construct_prompt(query: str, context: str) -> str:
        """Structured prompt engineering"""
        return f"""As a mental health professional, analyze this context:
        {context}
        
        User Query: {query}
        
        Analyze the user query with respect to the following elements:
        1. Empathetic acknowledgement
        2. Evidence-based suggestions
        3. Crisis resources if needed
        4. Non-judgemental tone
        
        After a critical analysis, provide a response that is conversational, empathetic, supportive, and informative. 
        
        Make sure you read the emotional context and provide a response that is appropriate, not offensive and helpful.
    
        """

    def _fallback_response(self, query: str) -> ConversationResponse:
        """Graceful degradation response"""
        return ConversationResponse(
            response="I'm having trouble accessing my resources. Please try again later.",
            context="",
            web_context="",
            vector_db_context="",
            query=query
        )


# Usage Example
if __name__ == "__main__":
    conversation = LLMConversation()
    response = conversation.process_query("I feel really sad today")
    print(response)