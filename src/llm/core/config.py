from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY")
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 5432
    REDIS_DB: str = "therapy_bot"
    REDIS_USER: str = "redis"
    REDIS_PASSWORD: str = ""
    SESSION_TTL: int = 86400
    MAX_RETRIES: int = 3
    SAFETY_THRESHOLD: float = 0.95
    TAVILY_MAX_RESULTS: int = 3
    TAVILY_INCLUDE_IMAGES: bool = False
    TAVILY_INCLUDE_ANSWER: bool = True
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2")
    LANGCHAIN_ENDPOINT: str = os.getenv("LANGCHAIN_ENDPOINT")
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY")
    SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI: str = os.getenv("SPOTIFY_REDIRECT_URI")
    
    class Config:
        env_file = ".env"

settings = Settings()