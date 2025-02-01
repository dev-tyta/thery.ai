import time
import uuid
from typing import Optional, Tuple
from .redis_connection import RedisConnection
from src.llm.core.config import settings

class SessionManager:
    def __init__(self):
        self.redis = RedisConnection().client
        
    def generate_ids(self, existing_user_id: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate or validate user/session IDs
        Returns: (user_id, session_id)
        """
        user_id = self._get_or_create_user_id(existing_user_id)
        session_id = self._create_session(user_id)
        return user_id, session_id

    def _get_or_create_user_id(self, existing_user_id: Optional[str]) -> str:
        if existing_user_id:
            if self.redis.exists(f"user:{existing_user_id}"):
                return existing_user_id
            # If invalid existing ID, generate new
            return str(uuid.uuid4())
        return str(uuid.uuid4())

    def _create_session(self, user_id: str) -> str:
        session_id = str(uuid.uuid4())
        # Store session metadata
        self.redis.hset(f"session:{session_id}", mapping={
            "user_id": user_id,
            "created_at": str(time.time()),
            "activity": str(time.time())
        })
        # Set TTL (24 hours by default)
        self.redis.expire(f"session:{session_id}", settings.SESSION_TTL)
        # Link to user
        self.redis.sadd(f"user:{user_id}:sessions", session_id)
        return session_id

    def validate_session(self, session_id: str) -> Optional[str]:
        """Returns user_id if valid session"""
        if self.redis.exists(f"session:{session_id}"):
            # Update last activity
            self.redis.hset(f"session:{session_id}", "activity", str(time.time()))
            return self.redis.hget(f"session:{session_id}", "user_id")
        return None