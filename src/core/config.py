import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings # Use pydantic_settings for BaseSettings
from typing import Optional, List

# Load environment variables from a .env file if it exists
# This allows you to configure settings without hardcoding them
load_dotenv()

class Settings(BaseSettings):
    # Database connection URL
    # Example: postgresql+asyncpg://user:password@host:port/database
    # Using individual components from your provided config
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT: int = os.getenv("POSTGRES_PORT", 5432)
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "theryai_db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "user") # Assuming user/password are needed for URI
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password") # Assuming user/password are needed for URI

    # Construct DATABASE_URL from components if POSTGRES_URI is not set
    # Prioritize POSTGRES_URI if provided, otherwise build from components
    POSTGRES_URI: Optional[str] = os.getenv("POSTGRES_URI")
    DATABASE_URL: str = POSTGRES_URI if POSTGRES_URI else f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


    # Redis connection details
    # Using individual components from your provided config
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = os.getenv("REDIS_PORT", 6379)
    REDIS_DB: int = os.getenv("REDIS_DB", 0) # Added REDIS_DB from your config
    REDIS_USERNAME: Optional[str] = os.getenv("REDIS_USERNAME") # Optional username
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD") # Optional password

    # Construct REDIS_URL from components
    # Example: redis://[[username]:password@]host[:port][/db]
    REDIS_URL: str = f"redis://{f'{REDIS_USERNAME}:' if REDIS_USERNAME else ''}{f'{REDIS_PASSWORD}@' if REDIS_PASSWORD else ''}{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"


    # JWT Secret Key for encoding/decoding tokens
    # IMPORTANT: Change this to a strong, random secret in production!
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-me")
    ALGORITHM: str = "HS256" # Algorithm used for JWT signing
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Access token expiration time in minutes

    # Session TTL for Redis (from your config)
    SESSION_TTL: int = os.getenv("SESSION_TTL", 86400) # Default to 24 hours

    # AI/LLM related settings (from your config)
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")
    MAX_RETRIES: int = os.getenv("MAX_RETRIES", 3)
    MAX_TOKENS: int = os.getenv("MAX_TOKENS", 200)
    SAFETY_THRESHOLD: float = os.getenv("SAFETY_THRESHOLD", 0.95)
    TAVILY_MAX_RESULTS: int = os.getenv("TAVILY_MAX_RESULTS", 3)
    TAVILY_INCLUDE_IMAGES: bool = os.getenv("TAVILY_INCLUDE_IMAGES", False)
    TAVILY_INCLUDE_ANSWER: bool = os.getenv("TAVILY_INCLUDE_ANSWER", True)
    LANGCHAIN_API_KEY: Optional[str] = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_TRACING_V2: Optional[str] = os.getenv("LANGCHAIN_TRACING_V2")
    LANGCHAIN_ENDPOINT: Optional[str] = os.getenv("LANGCHAIN_ENDPOINT")
    LANGSMITH_API_KEY: Optional[str] = os.getenv("LANGSMITH_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    CLAUDE_API_KEY: Optional[str] = os.getenv("CLAUDE_API_KEY")

    # Spotify settings (from your config)
    SPOTIFY_CLIENT_ID: Optional[str] = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET: Optional[str] = os.getenv("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI: Optional[str] = os.getenv("SPOTIFY_REDIRECT_URI")

    # Telegram settings (from your config)
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")

    # CORS settings (adjust as needed for your frontend origin)
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:8000", # Example frontend development server
        "http://localhost:8080",
        "http://localhost:3000",
        # Add your production frontend URL here
    ]

    class Config:
        # Allow .env file to be used
        env_file = ".env"
        # Case-insensitive matching for environment variables
        env_case_sensitive = False
        # Ignore extra fields not defined in the model
        extra = 'ignore'


settings = Settings()

# Example of how to use it:
# print(settings.DATABASE_URL)
# print(settings.SECRET_KEY)
# print(settings.REDIS_URL)
