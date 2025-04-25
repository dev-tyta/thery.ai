from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from datetime import datetime
from src.models.schemas import ConversationResponse, SessionData
from src.utils.logging import TheryBotLogger
from src.memory.history import RedisHistory
from src.memory.memory_manager import RedisMemoryManager
from src.memory.session_manager import SessionManager
from src.services.llm.agents.conversation_agent import ConversationAgent

router = APIRouter(
    prefix="/api/v1",
    tags=["TheryAI Core Services"],
    responses={500: {"description": "Internal Server Error"}}
)

# Initialize core components
session_manager = SessionManager()
memory_manager = RedisMemoryManager()
history = RedisHistory()
logger = TheryBotLogger()
conversation_agent = ConversationAgent()

@router.post("/users", response_model=dict)
async def create_user():
    """Create a new user ID"""
    try:
        user_id, _ = session_manager.generate_ids()
        return {"user_id": user_id}
    except Exception as e:
        logger.error(f"User creation failed: {str(e)}")
        raise HTTPException(500, "User creation failed")

@router.post("/sessions", response_model=SessionData)
async def create_session(user_id: str):
    """Create a new session ID for a user"""
    try:
        _, session_id = session_manager.generate_ids(existing_user_id=user_id)
        return SessionData(
            user_id=user_id,
            session_id=session_id,
            is_new_user=False,
            is_new_session=True
        )
    except Exception as e:
        logger.error(f"Session creation failed: {str(e)}")
        raise HTTPException(500, "Session creation failed")

@router.get("/sessions/{session_id}/messages", response_model=List[ConversationResponse])
async def get_messages(session_id: str, limit: int = 50):
    """Get message history for a session"""
    try:
        if not session_manager.validate_session(session_id):
            raise HTTPException(404, "Session not found")
            
        messages = history.get_conversation_history(session_id, limit=limit)
        return [msg["response"] for msg in messages]
    except Exception as e:
        logger.error(f"Message retrieval failed: {str(e)}")
        raise HTTPException(500, "Message retrieval failed")

@router.post("/sessions/{session_id}/messages", response_model=ConversationResponse)
async def create_message(
    session_id: str,
    message: str,
    background_tasks: BackgroundTasks
):
    """Process and store a new message"""
    try:
        user_id = session_manager.validate_session(session_id)
        if not user_id:
            raise HTTPException(404, "Invalid session")
            
        response = await conversation_agent.process_async(
            query=message,
            session_data=SessionData(
                user_id=user_id,
                session_id=session_id,
                is_new_user=False,
                is_new_session=False
            )
        )
        
        background_tasks.add_task(
            memory_manager.store_conversation,
            session_id,
            datetime.now().isoformat(),
            response
        )
        
        return response
    except Exception as e:
        logger.error(f"Message processing failed: {str(e)}")
        raise HTTPException(500, "Message processing failed")