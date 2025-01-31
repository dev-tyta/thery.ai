from typing import Dict, List
from src.music.clients.spotify_client import SpotifyClient
from src.music.config.settings import logger, SpotifyConfig

class GenreMapper:
    """Maps emotions to appropriate genres"""
    
    def __init__(self, spotify_client: SpotifyClient):
        self.spotify = spotify_client
        self.genre_hierarchy = {
            "sad": ["blues", "soul", "acoustic"],
            "happy": ["pop", "dance", "disco"],
            "anxious": ["ambient", "classical"],
            "angry": ["rock", "metal"]
        }
        self.available_genres = self._load_available_genres()

    def _load_available_genres(self) -> List[str]:
        """Load available genres from Spotify"""
        return self.spotify.get_available_genres()

    def get_genres(self, emotion: str) -> List[str]:
        """Get appropriate genres for an emotion"""
        emotion_genres = self.genre_hierarchy.get(emotion, [])
        available = [genre for genre in emotion_genres if genre in self.available_genres]
        return available if available else ["pop"]



# Usage:
client = SpotifyClient(config=SpotifyConfig())
mapper = GenreMapper(client)
print(mapper.get_genres("happy"))
