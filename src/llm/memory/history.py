# File: history.py
import json
from src.llm.memory.pg_connection import PostgresConnection

class History:
    def __init__(self):
        self.pg_conn = PostgresConnection().connect()
        self._initialize_schema()

    def _initialize_schema(self):
        with self.pg_conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id SERIAL PRIMARY KEY,
                    chat_id VARCHAR(255) NOT NULL,
                    message_type VARCHAR(50),
                    message_content TEXT,
                    emotion_label VARCHAR(100),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.pg_conn.commit()

    def add_message(self, chat_id, message_type, message_content, emotion_label=None, metadata=None):
        with self.pg_conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO chat_history 
                (chat_id, message_type, message_content, emotion_label, metadata)
                VALUES (%s, %s, %s, %s, %s)
            ''', (chat_id, message_type, message_content, emotion_label, json.dumps(metadata or {})))
            self.pg_conn.commit()

    def get_messages(self, chat_id):
        with self.pg_conn.cursor() as cursor:
            cursor.execute('''
                SELECT message_type, message_content, emotion_label, metadata, created_at
                FROM chat_history
                WHERE chat_id = %s
                ORDER BY created_at ASC
            ''', (chat_id,))
            return [{
                'message_type': row[0],
                'message_content': row[1],
                'emotion_label': row[2],
                'metadata': row[3],
                'timestamp': row[4]
            } for row in cursor.fetchall()]

    def clear_history(self, chat_id):
        with self.pg_conn.cursor() as cursor:
            cursor.execute('DELETE FROM chat_history WHERE chat_id = %s', (chat_id,))
            self.pg_conn.commit()
