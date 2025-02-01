import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY")
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "therapy_bot"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    MAX_RETRIES: int = 3
    SAFETY_THRESHOLD: float = 0.95
    TAVILY_MAX_RESULTS: int = 3
    TAVILY_INCLUDE_IMAGES: bool = False
    TAVILY_INCLUDE_ANSWER: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()