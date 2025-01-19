import redis 
import os
from dotenv import load_dotenv

load_dotenv()

class RedisConnection:
    def __init__(self):
        self.host = os.getenv('REDIS_HOST', 'localhost')
        self.port = os.getenv('REDIS_PORT', 6379)
        self.db = os.getenv('REDIS_DB', 0)
        self.connection = None

    def connect(self):
        if not self.connection:
            self.connection = redis.Redis(host=self.host, port=self.port, db=self.db)

            return self.connection
        
        