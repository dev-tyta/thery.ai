import uuid
import textwrap
import logging
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent
from .emotion_agent import EmotionAgent
from .context_agent import ContextAgent
from src.llm.models.schemas import ConversationResponse, EmotionalAnalysis, ContextInfo
from src.llm.models.schemas import SessionData
from src.llm.memory.memory_manager import RedisMemoryManager
from src.llm.memory.session_manager import SessionManager
from src.llm.memory.history import RedisHistory

class ConversationAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.emotion_agent = EmotionAgent(llm=self.llm, history=self.history)
        self.context_agent = ContextAgent(llm=self.llm, history=self.history)
        self.memory_manager = RedisMemoryManager()
        self.session_manager = SessionManager()
        self.history = RedisHistory()
    
    def process(
        self,
        query: str,
        session_data: Optional[SessionData] = None
    ) -> ConversationResponse:
        """Process user query with emotional awareness and context"""
        # Generate or validate IDs
        if session_data:
            user_id = self.session_manager.validate_session(session_data.session_id)
            if user_id:
                # Existing valid session
                session_id = session_data.session_id
                is_new_session = False
            else:
                # Expired session, create new
                user_id, session_id = self.session_manager.generate_ids(session_data.user_id)
                is_new_session = True
        else:
            # New conversation
            user_id, session_id = self.session_manager.generate_ids()
            is_new_session = True

        chat_id = str(uuid.uuid4())
        # Analyze emotion
        emotion_analysis = self.emotion_agent.process(query)
        
        # Gather context
        context = self.context_agent.process(query)
        context = ContextInfo(
            query=context.query,
            web_context=context.web_context,
            vector_context=context.vector_context,
            combined_context=context.combined_context
        )

        history_context= self.history.get_full_context(session_id)
        
        combined_context = context.combined_context if context else None
        
        # Generate response
        response = self._generate_response(
            query=query,
            emotion_analysis=emotion_analysis,
            context=combined_context,
            chat_history=history_context
        )
        
        self.memory_manager.store_conversation(session_id, chat_id, response)
        self.history.add_conversation(session_id, chat_id, response)

        self._log_action(action="conversation", metadata={"query": query, "response": response}, level=logging.INFO, session_id=session_id, user_id=user_id)
        
        return ConversationResponse(
            session_data=SessionData(
                user_id=user_id,
                session_id=session_id,
                is_new_user=(session_data is None),
                is_new_session=is_new_session
            ),
            response=response,
            emotion_analysis=emotion_analysis,
            context=context,
            query=query
        )
    
    def _generate_response(
        self,
        query: str,
        emotion_analysis: Optional[EmotionalAnalysis],
        context: Optional[ContextInfo],
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
        prompt = f"""
                You are Thery AI, a compassionate virtual therapist who provides supportive, evidence-based advice and empathetic conversation. When generating your response, follow these steps internally:

                1. **Acknowledge the Emotional State:**  
                - Identify and validate the emotion expressed by the user.  
                - Use language that shows understanding and empathy.

                2. **Provide Evidence-Based Support:**  
                - Incorporate relevant research or common therapeutic techniques where applicable.  
                - Ensure that your advice is grounded in best practices.

                3. **Incorporate Context Appropriately:**  
                - Use the provided context (from previous interactions or additional background) to make your response more personalized and relevant.

                4. **Maintain a Supportive and Empathetic Tone:**  
                - Craft your response as if you were speaking with a friend who cares deeply about the user’s well-being.
                - Avoid clinical jargon; use accessible, warm, and encouraging language.

                5. **Include Specific Coping Strategies When Appropriate:**  
                - Offer actionable suggestions (like deep breathing, mindfulness, journaling, or seeking additional support) that the user can try.
                - Ask gentle follow-up questions to invite the user to share more, if needed.

                **Input Variables:**
                - **Chat History:** `{kwargs['chat_history']}`
                - **User Query:** `{kwargs['query']}`
                - **Emotional Analysis:** `{kwargs['emotion_analysis']}`
                - **Context:** `{kwargs['context']}`

                **Response Example:**
                - If the user says, “Hello,” start with a friendly greeting:  
                *"Hi there, I'm Thery AI. How can I help you today?"*

                - If the user later says, “I feel sad,” continue with:  
                *"I'm sorry to hear you're feeling sad. Can you tell me a bit more about what's been going on? Sometimes sharing details can help in understanding and easing your feelings."*

                Generate your final response by synthesizing these points into a natural, supportive message. Keep in mind that your internal chain-of-thought should guide you to consider the user's feelings, context, and the best evidence-based strategies before producing your answer.
        """

        return textwrap.dedent(prompt).strip()