from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class TrackRecommendation:
    uri: str
    name: str
    artist: str
    preview_url: Optional[str]
    audio_features: Dict

@dataclass
class RecommendationParameters:
    seed_genres: List[str]
    target_features: Dict
    limit: int = 20
    market: str = "US"