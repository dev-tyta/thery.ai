import redis
import logging
from src.llm.core.config import settings
from src.llm.utils.logging import TheryBotLogger

class RedisConnection:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_self()
        return cls._instance
    
    def _initialize_self(self) -> None:
        self.logger = TheryBotLogger()
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            username=settings.REDIS_USERNAME,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        try:
            self.redis.ping()
        except redis.ConnectionError as e:
            self.logger.log_interaction(
                interaction_type="redis_connection_failed",
                data={"error": str(e)},
                level=logging.ERROR
            )
            raise RuntimeError(f"Redis connection failed: {str(e)}")

    @property
    def client(self):
        if not self.redis.ping():
            self._initialize_self()
        return self.redis