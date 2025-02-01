from pydantic import BaseSettings

class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    TAVILY_API_KEY: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "therapy_bot"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()