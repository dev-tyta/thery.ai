from typing import Dict, Any, Optional
from .redis_connection import RedisConnection
from src.llm.models.schemas import ConversationResponse
import json
import time

class RedisMemoryManager:
    def __init__(self):
        self.redis = RedisConnection().client
    
    def store_conversation(self, session_id: str, chat_id: str, response: ConversationResponse) -> None:
        """
        Store complete conversation response with metadata
        """
        response_data = response.dict()
        timestamp = time.time()
        
        # Store in session-specific hash
        self.redis.hset(
            f"session:{session_id}:chats",
            chat_id,
            json.dumps({
                'response': response_data,
                'timestamp': timestamp
            })
        )
        
        # Update session metadata
        self.redis.hset(
            f"session:{session_id}",
            mapping={
                'last_chat_id': chat_id,
                'last_updated': str(timestamp)
            }
        )
    
    def get_conversation(self, session_id: str, chat_id: str) -> Optional[ConversationResponse]:
        """
        Retrieve specific conversation response
        """
        data = self.redis.hget(f"session:{session_id}:chats", chat_id)
        if data:
            return ConversationResponse(**json.loads(data)['response'])
        return None
    
    def get_session_conversations(self, session_id: str) -> Dict[str, Any]:
        """
        Get all conversations for a session
        """
        conversations = self.redis.hgetall(f"session:{session_id}:chats")
        return {
            chat_id: ConversationResponse(**json.loads(data)['response'])
            for chat_id, data in conversations.items()
        }
    
    def update_emotional_state(self, session_id: str, emotions: Dict[str, Any]) -> None:
        """
        Update emotional state tracking
        """
        self.redis.hset(
            f"session:{session_id}:state",
            'emotions',
            json.dumps(emotions)
        )
    
    def get_emotional_state(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve current emotional state
        """
        data = self.redis.hget(f"session:{session_id}:state", 'emotions')
        return json.loads(data) if data else {}