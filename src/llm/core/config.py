from dotenv import load_dotenv
import os
from typing import Optional
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # Gemini (primary LLM)
    GOOGLE_API_KEY: Optional[str] = None

    # Web search
    TAVILY_API_KEY: Optional[str] = None
    TAVILY_MAX_RESULTS: int = 3
    TAVILY_INCLUDE_IMAGES: bool = False
    TAVILY_INCLUDE_ANSWER: bool = True

    # Redis — prefer a full URL; fall back to individual components
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_USERNAME: Optional[str] = None
    REDIS_PASSWORD: Optional[str] = None

    # Postgres — passed as a full URL
    POSTGRES_URL: Optional[str] = None

    # Session
    SESSION_TTL: int = 86400

    # LLM generation knobs
    MAX_RETRIES: int = 3
    MAX_TOKENS: int = 2048
    SAFETY_THRESHOLD: float = 0.95

    # LangSmith tracing (optional)
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_TRACING_V2: Optional[str] = None
    LANGCHAIN_ENDPOINT: Optional[str] = None
    LANGSMITH_API_KEY: Optional[str] = None

    # Spotify
    SPOTIFY_CLIENT_ID: Optional[str] = None
    SPOTIFY_CLIENT_SECRET: Optional[str] = None
    SPOTIFY_REDIRECT_URI: Optional[str] = None

    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None

    @property
    def effective_redis_url(self) -> str:
        """Return REDIS_URL if set, otherwise build from individual components."""
        if self.REDIS_URL:
            return self.REDIS_URL
        auth = ""
        if self.REDIS_USERNAME and self.REDIS_PASSWORD:
            auth = f"{self.REDIS_USERNAME}:{self.REDIS_PASSWORD}@"
        elif self.REDIS_PASSWORD:
            auth = f":{self.REDIS_PASSWORD}@"
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()