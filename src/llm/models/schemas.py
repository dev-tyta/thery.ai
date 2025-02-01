from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class EmotionalAnalysis(BaseModel):
    primary_emotion: str
    intensity: int = Field(..., ge=1, le=10)
    secondary_emotions: List[str]
    triggers: List[str]
    coping_strategies: List[str]
    confidence_score: float = Field(..., ge=0, le=1)

class ContextInfo(BaseModel):
    query: str
    web_context: str
    vector_context: str
    combined_context: str
    relevance_score: float = Field(..., ge=0, le=1)

class SessionData(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    session_id: str = Field(..., description="Current session identifier")
    is_new_user: bool = Field(False, description="Flag for new user detection")
    is_new_session: bool = Field(False, description="Flag for new session detection")

class ConversationResponse(BaseModel):
    session_data: SessionData
    response: str = Field(..., description="Primary assistant response")
    emotion_analysis: EmotionalAnalysis
    context: ContextInfo
    query: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    safety_level: str = Field(..., description="Assessment of response safety")
    suggested_resources: List[str] = Field(default_factory=list)