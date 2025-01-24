from pydantic import BaseModel
from typing import List, Optional, Type, Any, Dict

from src.llm.core import TheTherapistLLM
from src.memory.history import History

class ConvoResponse(BaseModel):
    response: str
    context: str
    web_context: str
    vector_db_context: str
    query: str


class LLMConvo:
    """
    Conversational Interface for TheTherapist LLM

    Attributes:
        llm (TheTherapistLLM): The LLM instance
        history: Set Up for saving the conversation history.
    """

    llm: Optional[TheTherapistLLM] = None
    history: Optional[History] = None


    def init(self, query: str, chat_history: list = None):
        """
        Initialize the LLM with the given configuration.

        Args:
            query: The input query
            chat_history: List of previous chat messages
        """
        self.llm = TheTherapistLLM()
        self.tavily_tool, self.vector_search = self.llm.initialize_tools()
        self.history = History()
        self.query = query
        self.chat_history = chat_history


    def web_search(self, query: str) -> str:
        """Perform web search using Tavily"""
        web_results = self.tavily_tool[0].invoke(query)
        web_context = "\n".join([result["content"] for result in web_results])
        return web_context
    

    def db_retriever(self, query):
        """Retrieve context from vector DB"""
        context = self.vector_search(self, query)
        return context


    def get_response(self, query: str, chat_history: list = None) -> str:
        """Get response from LLM using both vector DB and web search"""
        if chat_history is None:
            chat_history = []
        
        # retriever and web search context
        retriever_context = self.db_retriever(query)
        web_context = self.web_search(query)

        
        # Combine contexts
        full_context = f"Vector DB context:\n{retriever_context}\n\nWeb search context:\n{web_context}"
        
        # Format prompt
        prompt = f"""As a mental health assistant, use the following context to answer:
        {full_context}
        
        User question: {query}
        
        Please provide a helpful, empathetic response based on the available information."""
        
        # Get LLM response
        response = self.llm.send_query(prompt)
        
        return response
    
    def save_to_history(self, chat_id, prompt, response, emotion_label, other_info):
        self.history.add_message(chat_id=chat_id, message_content= prompt, emotion_label=emotion_label, metadata=other_info)
        


# Example usage
model = ConvoResponse()
response = model.get_response("How can I manage anxiety?")
print(response)