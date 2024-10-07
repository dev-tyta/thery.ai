import json
from src.redis_connection import RedisConnection


class History:
    def __init__(self):
        self.redis_conn = RedisConnection().connect()

    def add_message(self, chat_id, message_type, message_content, emotion_label=None, metadata=None):
        message = {
            'message_type': message_type,
            'message_content': message_content,
            'emotion_label': emotion_label,
            'metadata': metadata or {}
        }
        self.redis_conn.rpush(chat_id, json.dumps(message))

    def get_messages(self, chat_id):
        messages = self.redis_conn.lrange(chat_id, 0, -1)
        return [json.loads(message) for message in messages]
    
    def clear_history(self, chat_id):
        self.redis_conn.delete(chat_id)
