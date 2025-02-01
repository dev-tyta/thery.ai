import redis
from src.llm.core.config import settings
from src.llm.utils.logging import TherapyBotLogger

class RedisConnection:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance
    
    def _initialize_self(self) -> None:
        self.logger = TherapyBotLogger()
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        try:
            self.redis.ping()
        except redis.ConnectionError as e:
            self.logger.log_interaction(
                "redis_connection_failed",
                {"error": str(e)},
                level="ERROR"
            )
            raise RuntimeError(f"Redis connection failed: {str(e)}")

    @property
    def client(self):
        if not self.redis.ping():
            self._initialize_connection()
        return self.redis