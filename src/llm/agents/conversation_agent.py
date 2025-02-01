# src/agents/conversation_agent.py
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent
from .emotion_agent import EmotionAgent
from .context_agent import ContextAgent
from src.models.schemas import ConversationResponse

class ConversationAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.emotion_agent = EmotionAgent(llm=self.llm, history=self.history)
        self.context_agent = ContextAgent(llm=self.llm, history=self.history)
    
    def process(
        self,
        query: str,
        chat_history: Optional[List[Dict]] = None
    ) -> ConversationResponse:
        """Process user query with emotional awareness and context"""
        # Analyze emotion
        emotion_analysis = self.emotion_agent.process(query)
        
        # Gather context
        context = self.context_agent.process(query)
        
        # Generate response
        response = self._generate_response(
            query=query,
            emotion_analysis=emotion_analysis,
            context=context,
            chat_history=chat_history
        )
        
        return ConversationResponse(
            response=response,
            emotion_analysis=emotion_analysis,
            context=context,
            query=query
        )
    
    def _generate_response(
        self,
        query: str,
        emotion_analysis: Dict[str, Any],
        context: Dict[str, str],
        chat_history: Optional[List[Dict]]
    ) -> str:
        prompt = self._construct_response_prompt(
            query=query,
            emotion_analysis=emotion_analysis,
            context=context,
            chat_history=chat_history
        )
        
        response = self.llm.generate(prompt)
        return response.content.strip()
    
    def _construct_response_prompt(self, **kwargs) -> str:
        # Implement sophisticated prompt construction
        return f"""
        Given the following information:
        
        User Query: {kwargs['query']}
        Emotional Analysis: {kwargs['emotion_analysis']}
        Context: {kwargs['context']['combined_context']}
        
        Generate a response that:
        1. Acknowledges the emotional state
        2. Provides relevant, evidence-based support
        3. Incorporates context appropriately
        4. Maintains a supportive and empathetic tone
        5. Includes specific coping strategies when appropriate
        """