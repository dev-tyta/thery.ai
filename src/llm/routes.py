from fastapi import APIRouter, Depends, HTTPException
from src.llm.agents.conversation_agent import ConversationAgent
from src.llm.models.schemas import ConversationResponse, SessionData
from src.llm.utils.logging import TheryBotLogger
from src.llm.memory.history import RedisHistory
from src.llm.memory.memory_manager import RedisMemoryManager
from src.llm.memory.session_manager import SessionManager
from src.llm.core.config import settings


router = APIRouter(
    prefix="api/v1",
    tags=["TheryAI Services"],
    responses={
        200: {"description": "Success"},
        400: {"description": "Bad Request"},
        404: {"description": "Not found"},
        500: {"description": "Internal Server Error"}
        },
)




@router.get("/{session_id}")
def get_user_id(session_id: str):
    

