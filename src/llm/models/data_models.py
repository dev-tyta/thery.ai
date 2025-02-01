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
    web_context: str
    vector_context: str
    combined_context: str
    relevance_score: float = Field(..., ge=0, le=1)

class ConversationResponse(BaseModel):
    response: str = Field(..., description="Primary assistant response")
    emotion_analysis: EmotionalAnalysis
    context: ContextInfo
    query: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    safety_level: str = Field(..., description="Assessment of response safety")
    suggested_resources: List[str] = Field(default_factory=list)