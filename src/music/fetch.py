#TODO:Work on the fetching music from Spotify. Figure out a way to find music based on the emotion detected during the conversation.
#TODO: Implement a smooth algorithm to sync music without a fail.


import json
import time
import spotipy
import random
from spotipy.oauth2 import SpotifyClientCredentials
import os

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_SECRET")

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

