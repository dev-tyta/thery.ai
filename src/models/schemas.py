from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, EmailStr, Field

# --- User Schemas ---

class UserBase(BaseModel):
    """Base schema for User."""
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    """Schema for User creation (includes password)."""
    password: str = Field(..., min_length=8) # Password is required and has a min length

class User(UserBase):
    """Schema for reading User data (excludes password)."""
    user_id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None # Updated_at might be None initially

    class Config:
        # Allow SQLAlchemy models to be converted to this schema
        from_attributes = True # Use from_orm=True in older Pydantic versions


# --- Session Schemas ---

class SessionBase(BaseModel):
    """Base schema for Session."""
    # No fields here initially, as session_id and user_id are generated/linked
    pass

class SessionCreate(BaseModel):
    """Schema for creating a Session (requires user_id)."""
    user_id: uuid.UUID

class Session(SessionBase):
    """Schema for reading Session data."""
    session_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    last_active: datetime

    class Config:
        from_attributes = True


# --- Message Schemas ---
class EmotionalAnalysis(BaseModel):
    primary_emotion: str
    intensity: int = Field(..., ge=1, le=10)
    secondary_emotions: List[str]
    triggers: List[str]
    coping_strategies: List[str] = []
    confidence_score: float = Field(..., ge=0, le=1)

    class Config:
        # Allow arbitrary types for flexibility with JSONB
        arbitrary_types_allowed = True

class MessageBase(BaseModel):
    """Base schema for Message."""
    sender: str # 'user' or 'bot'
    text: str

class MessageCreate(MessageBase):
    """Schema for creating a Message (sent from frontend)."""
    # Frontend sends sender and text
    pass

class Message(MessageBase):
    """Schema for reading Message data (includes backend-generated fields)."""
    message_id: uuid.UUID
    session_id: uuid.UUID
    timestamp: datetime
    emotional_analysis: Optional[EmotionalAnalysis] = None # Optional analysis data
    suggested_actions: Optional[List[str]] = None # Optional list of suggested actions

    class Config:
        from_attributes = True
        # Allow arbitrary types for flexibility with JSONB fields
        arbitrary_types_allowed = True


# --- Authentication Schemas ---

class Token(BaseModel):
    """Schema for the JWT token response."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for the data contained within the JWT token."""
    user_id: Optional[uuid.UUID] = None # User ID in the token payload

class LoginRequest(BaseModel):
    """Schema for the login request body."""
    email: EmailStr
    password: str

class ContextInfo(BaseModel):
    query: str
    web_context: str = ""
    vector_context: List[str] = Field(default_factory=list)
    combined_context: str = ""

class SessionData(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    session_id: str = Field(..., description="Current session identifier")
    is_new_user: bool = Field(False, description="Flag for new user detection")
    is_new_session: bool = Field(False, description="Flag for new session detection")

class ConversationResponse(BaseModel):
    session_data: SessionData
    response: str = Field(..., description="Primary assistant response")
    emotion_analysis: EmotionalAnalysis
    context: ContextInfo = Field(default_factory=ContextInfo)
    query: str
    safety_level: str = Field("unknown", description="Assessment of response safety")  # Default value
    suggested_resources: List[str] = Field(default_factory=list)