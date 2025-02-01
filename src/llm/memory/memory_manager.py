from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from src.llm.utils.database import DatabaseManager
from src.llm.utils.logging import TherapyBotLogger

class MemoryManager:
    """Centralized memory management system"""
    
    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        logger: Optional[TherapyBotLogger] = None
    ):
        self.db = db_manager or DatabaseManager()
        self.logger = logger or TherapyBotLogger()
        self._initialize_tables()
    
    def _initialize_tables(self) -> None:
        """Initialize necessary database tables"""
        with self.db.get_cursor() as cursor:
            # Create conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'::jsonb
                )
            """)
            
            # Create messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    conversation_id INTEGER REFERENCES conversations(id),
                    message_type VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    emotions JSONB DEFAULT '{}'::jsonb,
                    context JSONB DEFAULT '{}'::jsonb,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create user_state table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_state (
                    user_id VARCHAR(255) PRIMARY KEY,
                    emotional_state JSONB DEFAULT '{}'::jsonb,
                    context_history JSONB DEFAULT '{}'::jsonb,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def store_message(
        self,
        user_id: str,
        conversation_id: int,
        message_type: str,
        content: str,
        emotions: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> int:
        """Store a new message with associated data"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO messages 
                (conversation_id, message_type, content, emotions, context)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (conversation_id, message_type, content, emotions, context))
            
            message_id = cursor.fetchone()['id']
            
            # Update last interaction time
            cursor.execute("""
                UPDATE conversations 
                SET last_interaction = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (conversation_id,))
            
            return message_id
    
    def get_conversation_history(
        self,
        user_id: str,
        limit: int = 10,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Retrieve recent conversation history"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT m.* 
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                WHERE c.user_id = %s
                AND m.created_at > NOW() - INTERVAL '%s hours'
                ORDER BY m.created_at DESC
                LIMIT %s
            """, (user_id, hours, limit))
            
            return cursor.fetchall()
    
    def update_user_state(
        self,
        user_id: str,
        emotional_state: Dict[str, Any],
        context_history: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update user's emotional state and context"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_state 
                (user_id, emotional_state, context_history, last_updated)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) DO UPDATE
                SET emotional_state = %s,
                    context_history = COALESCE(%s, user_state.context_history),
                    last_updated = CURRENT_TIMESTAMP
            """, (user_id, emotional_state, context_history,
                 emotional_state, context_history))