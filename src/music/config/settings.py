import os
from dataclasses import dataclass
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SpotifyConfig:
    client_id: str = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret: str = os.getenv("SPOTIFY_CLIENT_SECRET")
    market: str = "US"
    max_retries: int = 3
    
    def validate(self):
        if not self.client_id or not self.client_secret:
            raise ValueError("Missing Spotify credentials in environment")