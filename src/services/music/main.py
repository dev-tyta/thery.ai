from abc import ABC, abstractmethod
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Dict, List, Optional
import os
import logging
from dataclasses import dataclass
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# -------------------------
# Data Structures
# -------------------------

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

# -------------------------
# Core Interfaces
# -------------------------

class IMusicRecommendationStrategy(ABC):
    @abstractmethod
    def generate_recommendations(self, emotion: str, context: Dict) -> List[TrackRecommendation]:
        pass

class IAudioAnalyzer(ABC):
    @abstractmethod
    def analyze_track(self, track_uri: str) -> Dict:
        pass

# -------------------------
# Spotify Client
# -------------------------

class SpotifyClient:
    """Handles Spotify authentication and basic API operations"""
    
    def __init__(self):
        self.client_credentials_manager = SpotifyClientCredentials(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
        )
        self.client = Spotify(client_credentials_manager=self.client_credentials_manager)
    
    def get_recommendations(self, params: RecommendationParameters) -> List[Dict]:
        """Base recommendation API call"""
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

# -------------------------
# Emotion Mapping System
# -------------------------

class EmotionAudioProfile:
    """Maps emotions to audio characteristics with cultural adaptation"""
    
    def __init__(self):
        self.base_profiles = {
            "sad": {"target_valence": 0.2, "target_energy": 0.3},
            "happy": {"target_valence": 0.8, "target_energy": 0.7},
            "anxious": {"target_valence": 0.5, "target_energy": 0.4},
            "angry": {"target_valence": 0.3, "target_energy": 0.8}
        }
        
        self.cultural_adjustments = {
            "US": {"happy": {"target_danceability": 0.8}},
            "JP": {"happy": {"target_danceability": 0.6}}
        }

    def get_profile(self, emotion: str, country: str = "US") -> Dict:
        """Get culturally adjusted audio profile"""
        profile = self.base_profiles.get(emotion, {}).copy()
        profile.update(self.cultural_adjustments.get(country, {}).get(emotion, {}))
        return profile


class GenreMapper:
    """Hierarchical genre mapping system with fallbacks"""
    
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
        """Get valid Spotify genres"""
        return self.spotify.client.recommendation_genre_seeds()['genres']

    def get_genres(self, emotion: str) -> List[str]:
        """Get best available genres for emotion"""
        for genre in self.genre_hierarchy.get(emotion, []):
            if genre in self.available_genres:
                return [genre]
        return ["pop"]

# -------------------------
# AI Integration
# -------------------------

class LLMEnhancer:
    """Enhances recommendations using LLM context analysis"""
    
    def __init__(self):
        from langchain_google_genai import ChatGoogleGenerativeAI
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro")

    def enhance_params(self, context: Dict) -> Dict:
        """Analyze conversation context for musical attributes"""
        prompt = f"""
        Analyze this therapeutic context to suggest music parameters:
        {json.dumps(context, indent=2)}
        
        Return JSON with:
        - target_energy (0-1)
        - target_danceability (0-1)
        - target_tempo 
        - seed_artist (main artist name)
        - seed_track (main track name)
        """
        
        try:
            response = self.llm.invoke(prompt)
            return json.loads(response.content)
        except Exception as e:
            logger.warning(f"LLM enhancement failed: {str(e)}")
            return {}

# -------------------------
# Recommendation Engine
# -------------------------

class TherapeuticMusicRecommender(IMusicRecommendationStrategy):
    """Main recommendation engine with multiple strategies"""
    
    def __init__(self):
        self.spotify = SpotifyClient()
        self.audio_profiler = EmotionAudioProfile()
        self.genre_mapper = GenreMapper(self.spotify)
        self.llm_enhancer = LLMEnhancer()
        self.cache = RecommendationCache()

    def generate_recommendations(self, emotion: str, context: Dict) -> List[TrackRecommendation]:
        """Generate context-aware recommendations"""
        # Check cache first
        cache_key = self._generate_cache_key(emotion, context)
        if cached := self.cache.get(cache_key):
            return cached

        # Build parameters
        params = self._build_recommendation_params(emotion, context)
        
        # Get raw recommendations
        raw_tracks = self.spotify.get_recommendations(params)
        
        # Process and enrich tracks
        processed = self._process_tracks(raw_tracks)
        
        # Cache results
        self.cache.store(cache_key, processed)
        
        return processed

    def _build_recommendation_params(self, emotion: str, context: Dict) -> RecommendationParameters:
        """Construct recommendation parameters"""
        base_features = self.audio_profiler.get_profile(
            emotion, 
            context.get('user', {}).get('country', 'US')
        )
        
        llm_features = self.llm_enhancer.enhance_params(context)
        
        return RecommendationParameters(
            seed_genres=self.genre_mapper.get_genres(emotion),
            target_features={**base_features, **llm_features},
            market=context.get('user', {}).get('country', 'US'),
            limit=context.get('limit', 20)
        )

    def _process_tracks(self, raw_tracks: List[Dict]) -> List[TrackRecommendation]:
        """Convert raw tracks to enriched recommendations"""
        return [
            TrackRecommendation(
                uri=track['uri'],
                name=track['name'],
                artist=track['artists'][0]['name'],
                preview_url=track.get('preview_url'),
                audio_features=self.spotify.client.audio_features(track['uri'])[0]
            ) for track in raw_tracks
        ]

    def _generate_cache_key(self, emotion: str, context: Dict) -> str:
        """Generate unique cache key"""
        return f"{emotion}-{context.get('user', {}).get('id', 'anonymous')}"

# -------------------------
# Advanced Features
# -------------------------

class RecommendationCache:
    """LRU cache for recommendations"""
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
        self.order = []

    def get(self, key: str) -> Optional[List[TrackRecommendation]]:
        if key in self.cache:
            self.order.remove(key)
            self.order.append(key)
            return self.cache[key]
        return None

    def store(self, key: str, recommendations: List[TrackRecommendation]):
        if len(self.cache) >= self.max_size:
            oldest = self.order.pop(0)
            del self.cache[oldest]
        self.cache[key] = recommendations
        self.order.append(key)

class MoodTransitionEngine:
    """Creates playlists that transition between emotional states"""
    
    def __init__(self, recommender: TherapeuticMusicRecommender):
        self.recommender = recommender
        
    def create_transition_playlist(self, start_emotion: str, end_emotion: str, context: Dict) -> List[TrackRecommendation]:
        """Generate mood transition sequence"""
        steps = self._calculate_transition_steps(start_emotion, end_emotion)
        playlist = []
        
        for step in steps:
            context['transition_step'] = step
            playlist += self.recommender.generate_recommendations(
                emotion=step['emotion'],
                context=context
            )
            
        return playlist

    def _calculate_transition_steps(self, start: str, end: str) -> List[Dict]:
        """Determine intermediate emotional states"""
        transitions = {
            ('sad', 'happy'): [{'emotion': 'sad', 'intensity': 0.8}, 
                              {'emotion': 'neutral', 'intensity': 0.5},
                              {'emotion': 'happy', 'intensity': 0.7}],
            # Add other transition paths
        }
        return transitions.get((start, end), [])

# -------------------------
# Usage Example
# -------------------------

if __name__ == "__main__":
    # Initialize system
    recommender = TherapeuticMusicRecommender()
    
    # Sample context from therapy session
    context = {
        "user": {
            "id": "user123",
            "country": "US",
            "time_of_day": datetime.now().hour
        },
        "conversation": {
            "emotion": "anxious",
            "key_phrases": ["work stress", "sleep issues"],
            "therapist_notes": "Needs calming music with nature sounds"
        }
    }
    
    # Generate recommendations
    recommendations = recommender.generate_recommendations(
        emotion="anxious",
        context=context
    )
    
    # Output results
    print(f"Generated {len(recommendations)} tracks:")
    for track in recommendations[:3]:
        print(f"- {track.artist}: {track.name} ({track.audio_features['tempo']} BPM)")