import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB # Use JSONB for structured data


from database import Base # Import the declarative base

class User(Base):
    """SQLAlchemy model for the 'users' table."""
    __tablename__ = "users"

    # Use UUID as the primary key
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=True) # Optional name field

    # Timestamps for tracking creation and updates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Define relationship to sessions
    # 'sessions' will be a list of Session objects associated with this user
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

    # Representation for debugging
    def __repr__(self):
        return f"<User(user_id={self.user_id}, email='{self.email}')>"


class Session(Base):
    """SQLAlchemy model for the 'sessions' table."""
    __tablename__ = "sessions"

    # Use UUID as the primary key
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign key linking to the users table
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)

    # Timestamps for tracking creation and last activity
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Define relationship back to the user
    user = relationship("User", back_populates="sessions")

    # Define relationship to messages
    # 'messages' will be a list of Message objects in this session
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

    # Representation for debugging
    def __repr__(self):
        return f"<Session(session_id={self.session_id}, user_id={self.user_id})>"


class Message(Base):
    """SQLAlchemy model for the 'messages' table."""
    __tablename__ = "messages"

    # Use UUID as the primary key
    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign key linking to the sessions table
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id"), nullable=False)

    # Sender of the message ('user' or 'bot')
    sender = Column(String, nullable=False)
    # The message text content
    text = Column(Text, nullable=False)
    # Timestamp for when the message was created
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Store emotional analysis data as JSONB (PostgreSQL specific)
    # This allows storing structured JSON data directly
    emotional_analysis = Column(JSONB, nullable=True)
    # Store suggested actions as JSONB (array of strings)
    suggested_actions = Column(JSONB, nullable=True)

    # Define relationship back to the session
    session = relationship("Session", back_populates="messages")

    # Representation for debugging
    def __repr__(self):
        return f"<Message(message_id={self.message_id}, session_id={self.session_id}, sender='{self.sender}')>"
