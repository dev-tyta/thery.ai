from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime

from src.llm.agents.conversation_agent import ConversationAgent
from src.llm.models.schemas import ConversationResponse, SessionData
from src.llm.utils.logging import TheryBotLogger
from src.llm.memory.history import RedisHistory
from src.llm.memory.memory_manager import RedisMemoryManager
from src.llm.memory.session_manager import SessionManager
from src.llm.core.config import settings

router = APIRouter(
    prefix="/api/v1",
    tags=["TheryAI Services"],
    responses={
        200: {"description": "Success"},
        400: {"description": "Bad Request"},
        404: {"description": "Not found"},
        500: {"description": "Internal Server Error"}
    },
)

# Initialize managers
session_manager = SessionManager()
memory_manager = RedisMemoryManager()
history = RedisHistory()
logger = TheryBotLogger()
conversation_agent = ConversationAgent()

@router.post("/users", response_model=dict)
async def create_user():
    """Create a new user and return user_id"""
    try:
        user_id, _ = session_manager.generate_ids()
        return {"user_id": user_id}
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@router.get("/users/{user_id}/sessions", response_model=List[dict])
async def get_user_sessions(user_id: str):
    """Get all sessions for a user"""
    try:
        sessions = session_manager.get_user_sessions(user_id)
        return sessions
    except Exception as e:
        logger.error(f"Error fetching sessions for user {user_id}: {str(e)}")
        raise HTTPException(status_code=404, detail="User not found")

@router.post("/sessions", response_model=SessionData)
async def create_session(user_id: Optional[str] = None):
    """Create a new session"""
    try:
        user_id, session_id = session_manager.generate_ids(existing_user_id=user_id)
        return SessionData(
            user_id=user_id,
            session_id=session_id,
            is_new_user=(user_id is None),
            is_new_session=True
        )
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create session")

@router.get("/sessions/{session_id}", response_model=SessionData)
async def get_session(session_id: str):
    """Get session metadata"""
    try:
        user_id = session_manager.validate_session(session_id)
        if not user_id:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionData(
            user_id=user_id,
            session_id=session_id,
            is_new_user=False,
            is_new_session=False
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch session")

@router.get("/sessions/{session_id}/messages", response_model=List[ConversationResponse])
async def get_session_messages(
    session_id: str,
    limit: Optional[int] = 10
):
    """Get messages from a session"""
    try:
        if not session_manager.validate_session(session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = history.get_conversation_history(session_id, limit=limit)
        return [msg["response"] for msg in messages]
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching messages for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch messages")

@router.post("/sessions/{session_id}/messages", response_model=ConversationResponse)
async def create_message(
    session_id: str,
    message: str,
    background_tasks: BackgroundTasks
):
    """Create a new message in a session"""
    try:
        user_id = session_manager.validate_session(session_id)
        if not user_id:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = SessionData(
            user_id=user_id,
            session_id=session_id,
            is_new_user=False,
            is_new_session=False
        )
        
        response = await conversation_agent.process_async(
            query=message,
            session_data=session_data
        )
        
        # Store conversation asynchronously
        background_tasks.add_task(
            memory_manager.store_conversation,
            session_id,
            str(datetime.now().timestamp()),
            response
        )
        
        return response
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing message in session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process message")

@router.get("/sessions/{session_id}/memory", response_model=dict)
async def get_session_memory(session_id: str):
    """Get all memory data for a session"""
    try:
        if not session_manager.validate_session(session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        
        conversations = memory_manager.get_session_conversations(session_id)
        emotional_state = memory_manager.get_emotional_state(session_id)
        
        return {
            "conversations": conversations,
            "emotional_state": emotional_state
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching memory for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch memory")

@router.delete("/sessions/{session_id}", response_model=dict)
async def end_session(session_id: str):
    """End a session and clean up resources"""
    try:
        if not session_manager.validate_session(session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        
        history.clear_history(session_id)
        session_manager.end_session(session_id)
        
        return {"message": "Session ended successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error ending session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to end session")