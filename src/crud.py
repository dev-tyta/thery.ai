import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from datetime import datetime
from typing import Optional, List

from auth import security # Import password hashing utilities
from models import User, Session, Message # Import SQLAlchemy models
from schemas import UserCreate, SessionCreate, MessageCreate, EmotionalAnalysis # Import Pydantic schemas

# --- User CRUD Operations ---

async def get_user_by_email(db: AsyncSession, email: str):
    """Retrieve a user from the database by email."""
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID):
    """Retrieve a user from the database by ID."""
    result = await db.execute(select(User).filter(User.user_id == user_id))
    return result.scalars().first()


async def create_user(db: AsyncSession, user: UserCreate):
    """Create a new user in the database."""
    # Hash the password before storing it
    hashed_password = security.get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password, name=user.name)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user) # Refresh to get the generated user_id and timestamps
    return db_user

# TODO: Add user update and delete functions if needed


# --- Session CRUD Operations ---

async def create_session(db: AsyncSession, session: SessionCreate):
    """Create a new session in the database."""
    db_session = Session(user_id=session.user_id)

    db.add(db_session)
    await db.commit()
    await db.refresh(db_session) # Refresh to get the generated session_id and timestamps
    return db_session

async def get_session_by_id(db: AsyncSession, session_id: uuid.UUID):
    """Retrieve a session from the database by ID."""
    result = await db.execute(select(Session).filter(Session.session_id == session_id))
    return result.scalars().first()

async def get_user_sessions(db: AsyncSession, user_id: uuid.UUID):
    """Retrieve all sessions for a specific user, ordered by last active."""
    result = await db.execute(
        select(Session)
        .filter(Session.user_id == user_id)
        .order_by(Session.last_active.desc()) # Order by last active, newest first
    )
    return result.scalars().all()

# TODO: Add session update (e.g., update last_active) and delete functions


# --- Message CRUD Operations ---

async def create_message(
    db: AsyncSession,
    session_id: uuid.UUID,
    message: MessageCreate,
    emotional_analysis: Optional[EmotionalAnalysis] = None,
    suggested_actions: Optional[List[str]] = None
):
    """Create a new message in the database."""
    # Convert Pydantic EmotionalAnalysis schema to a dictionary for JSONB
    analysis_dict = emotional_analysis.model_dump() if emotional_analysis else None

    db_message = Message(
        session_id=session_id,
        sender=message.sender,
        text=message.text,
        emotional_analysis=analysis_dict,
        suggested_actions=suggested_actions
    )

    db.add(db_message)
    await db.commit()
    await db.refresh(db_message) # Refresh to get the generated message_id and timestamp
    return db_message

async def get_session_history(db: AsyncSession, session_id: uuid.UUID):
    """Retrieve all messages for a specific session, ordered by timestamp."""
    result = await db.execute(
        select(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.timestamp) # Order by timestamp, oldest first
    )
    return result.scalars().all()

# TODO: Add message update and delete functions if needed
