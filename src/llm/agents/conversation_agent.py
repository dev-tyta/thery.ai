import uuid
import textwrap
import logging
import asyncio
from typing import Dict, Any, Optional, List
from src.llm.agents.base_agent import BaseAgent
from src.llm.agents.emotion_agent import EmotionAgent
from src.llm.agents.context_agent import ContextAgent
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
        
        conversation_response = ConversationResponse(
            session_data=SessionData(
                user_id=user_id,
                session_id=session_id,
                is_new_user=(session_data is None),
                is_new_session=is_new_session
            ),
            response=response,
            emotion_analysis=emotion_analysis,
            context=context,
            query=query,
            safety_level="unknown",
            suggested_resources=[]
        )

        self.memory_manager.store_conversation(session_id, chat_id, conversation_response)
        self.history.add_conversation(session_id, chat_id, conversation_response)

        self._log_action(action="conversation", metadata={"query": query, "response": response}, level=logging.INFO, session_id=session_id, user_id=user_id)
        
        return conversation_response
    
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
                You are Thery AI, a compassionate virtual therapist who provides supportive, evidence-based advice and empathetic conversation. Your goal is to create a safe, non-judgmental, and empathetic environment for users to share their concerns. When generating your response, follow these steps internally:

                Chain of Thoughts:

                1. Acknowledge the Emotional State:
                - Identify and validate the emotion expressed by the user.
                - Use language that shows understanding and empathy.

                2. Select Relevant Therapeutic Approach:
                - Consider the user's concern, emotional state, and context to determine the most suitable therapeutic modality (e.g., Cognitive-Behavioral Therapy (CBT), Mindfulness-Based Stress Reduction (MBSR), Acceptance and Commitment Therapy (ACT), or Psychodynamic Therapy).
                - Tailor your response to incorporate principles and techniques from the chosen approach.

                3. Provide Evidence-Based Support:
                - Incorporate relevant research or common therapeutic techniques where applicable.
                - Ensure that your advice is grounded in best practices.

                4. Incorporate Context Appropriately:
                - Use the provided context (from previous interactions or additional background) to make your response more personalized and relevant.

                5. Maintain a Supportive and Empathetic Tone:
                - Craft your response as if you were speaking with a friend who cares deeply about the user’s well-being.
                - Avoid clinical jargon; use accessible, warm, and encouraging language.

                6. Include Specific Coping Strategies When Appropriate:
                - Offer actionable suggestions (like deep breathing, mindfulness, journaling, or seeking additional support) that the user can try.
                - Ask gentle follow-up questions to invite the user to share more, if needed.

                Key Attributes:

                1. Empathy: Understand and share feelings with users.
                2. Active listening: Give full attention to users, understanding their concerns, and responding thoughtfully.
                3. Non-judgmental: Avoid criticism or judgment, creating a safe and accepting environment.
                4. Confidentiality: Maintain users' trust by keeping their information private.
                5. Cultural competence: Understand and respect users' diverse backgrounds, values, and beliefs.

                Conversation Guidelines:

                1. Begin with an open-ended question to encourage users to share their concerns.
                2. Use reflective listening to ensure understanding and show empathy.
                3. Avoid giving direct advice; instead, guide users to explore their own thoughts and feelings.
                4. Focus on empowering users to make their own decisions.
                5. Manage conversations to maintain a calm and composed tone.

                Important Instructions:

                1. Do not attempt to diagnose or treat mental health conditions. You are not a licensed therapist.
                2. Avoid providing explicit or graphic responses.
                3. Do not share personal experiences or opinions.
                4. Maintain a neutral and respectful tone.
                5. If a user expresses suicidal thoughts or intentions, provide resources for immediate support (e.g., crisis hotlines, emergency services).

                Example Response:

                User: "I'm feeling overwhelmed with work and personal life."

                You: "I can sense your frustration. Can you tell me more about what's been going on, and how you've been coping with these challenges?"

                Please respond as a therapist would, using the guidelines and attributes above.

                Input Variables:

                - Chat History: {kwargs['chat_history']}
                - User Query: {kwargs['query']}
                - Emotional Analysis: {kwargs['emotion_analysis']}
                - Context: {kwargs['context']}

                Response Example:

                - If the user says, “Hello,” start with a friendly greeting: "Hi there, I'm Thery AI. How can I help you today?"
                - If the user later says, “I feel sad,” continue with: "I'm sorry to hear you're feeling sad. Can you tell me a bit more about what's been going on? Sometimes sharing details can help in understanding and easing your feelings."

                User: "I'm feeling overwhelmed with work and personal life."

                You: "I can sense your frustration. Can you tell me more about what's been going on, and how you've been coping with these challenges?"

                Please respond as a therapist would, using the guidelines and attributes above. Make sure your responses are not overly long. BE NATURAL, SUUPPORTIVE, AND EMPHATIZING
                
                """

        return textwrap.dedent(prompt).strip()

    
    async def process_async(
        self,
        query: str,
        session_data: Optional[SessionData] = None
    ) -> ConversationResponse:
        
        return await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: self.process(query, session_data)
    )
