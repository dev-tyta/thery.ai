import json
import time
from datetime import timedelta
from typing import List, Dict, Any, Optional
from .redis_connection import RedisConnection
from src.llm.models.schemas import ConversationResponse
from src.llm.core.config import settings

class RedisHistory:
    def __init__(self, session_ttl: int = settings.SESSION_TTL):
        self.redis = RedisConnection().client
        self.session_ttl = session_ttl

    def add_conversation(self, session_id: str, chat_id: str, response: ConversationResponse) -> None:
        """
        Store complete conversation response in history
        """
        # Store in session-specific list
        self.redis.rpush(
            f"session:{session_id}:history",
            json.dumps({
                'chat_id': chat_id,
                'response': response.dict(),
                'timestamp': time.time()
            })
        )
        
        # Set TTL for session history
        self.redis.expire(f"session:{session_id}:history", self.session_ttl)
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history with optional limit
        """
        messages = self.redis.lrange(f"session:{session_id}:history", -limit, -1)
        return [
            {
                'chat_id': json.loads(msg)['chat_id'],
                'response': ConversationResponse(**json.loads(msg)['response']),
                'timestamp': json.loads(msg)['timestamp']
            }
            for msg in messages
        ]
    
    def get_full_context(self, session_id: str) -> str:
        """
        Generate conversation context string for LLM prompts
        """
        history = self.get_conversation_history(session_id)
        context_lines = []
        
        for entry in history:
            response = entry['response']
            context_lines.append(
                f"User: {response.query}\n"
                f"Therapist: {response.response}\n"
                f"Emotions: {response.emotion_analysis.primary_emotion} "
                f"(Intensity: {response.emotion_analysis.intensity})\n"
            )
        
        return "\n".join(context_lines)
    
    def clear_history(self, session_id: str) -> None:
        """
        Clear session history
        """
        self.redis.delete(f"session:{session_id}:history")