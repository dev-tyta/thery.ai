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
        try:
            self.redis = redis.from_url(
                settings.effective_redis_url,
                decode_responses=True
            )
            self.redis.ping()
        except redis.ConnectionError as e:
            self.logger.log_interaction(
                interaction_type="redis_connection_failed",
                data={"error": str(e)},
                level=logging.ERROR
            )
            raise RuntimeError(f"Redis connection failed: {str(e)}")

    @property
    def client(self) -> redis.Redis:
        try:
            self.redis.ping()
        except Exception:
            self._initialize_self()
        return self.redis