from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Dict, List
from src.music.config.settings import SpotifyConfig, logger
from src.music.models.data_models import RecommendationParameters

class SpotifyClient:
    """Handles Spotify authentication and API operations"""

    def __init__(self, config: SpotifyConfig):
        self.config = config
        self.config.validate()
        self.authenticate()

    def authenticate(self):
        """Authenticate and set up the Spotify client"""
        self.client_credentials_manager = SpotifyClientCredentials(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret
        )
        self.client = Spotify(client_credentials_manager=self.client_credentials_manager)

    def get_recommendations(self, params: RecommendationParameters) -> List[Dict]:
        """Get track recommendations from Spotify"""
        try:
            response = self.client.recommendations(
                seed_genres=params.seed_genres,
                target_features=params.target_features,
                limit=params.limit,
                market=params.market
            )
            return response['tracks']
        except Exception as e:
            logger.error(f"Recommendation failed: {str(e)}")
            raise

    def refresh_authentication(self):
        """Refresh authentication and reinitialize the client"""
        try:
            self.authenticate()
        except Exception as e:
            logger.error(f"Failed to refresh authentication: {str(e)}")
            raise

    def get_available_genres(self) -> List[str]:
        """Get available genre seeds from Spotify"""
        try:
            self.refresh_authentication()  # Ensure fresh authentication
            response = self.client.recommendation_genre_seeds()
            logger.info(f"Available genres: {response}")
            return response.get('genres', [])
        except Exception as e:
            logger.error(f"Failed to fetch genres: {str(e)}")
            return []

    def get_audio_features(self, track_uri: str) -> Dict:
        """Get audio features for a track"""
        try:
            return self.client.audio_features(track_uri)[0] or {}
        except Exception as e:
            logger.error(f"Failed to fetch audio features: {str(e)}")
            return {}


# Usage:
spotify_client = SpotifyClient(config=SpotifyConfig())
params = RecommendationParameters(
    seed_genres=["pop", "rock"], 
    target_features={"danceability": 0.7, "energy": 0.6},
    limit=10,
    market="US"
)

print(params)  # Debugging
recommendations = spotify_client.get_recommendations(params)
print(recommendations)
