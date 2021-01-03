import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

class Client:
    def __init__(self):
        load_dotenv()
        self.cid = os.getenv('CLIENT_ID')
        self.secret = os.getenv('SECRET_ID')
        self.client_credentials_manager = SpotifyClientCredentials(client_id=self.cid, client_secret=self.secret)
        self.sp = spotipy.Spotify(client_credentials_manager = self.client_credentials_manager)

    def find(self, song_name):
        song = self.sp.search(q=song_name, type="track", limit=1)
        name = song["tracks"]["items"][0]["name"]
        album = song["tracks"]["items"][0]["album"]["name"]
        artist = song["tracks"]["items"][0]["artists"][0]["name"]

        return name, album, artist

class Song:
    def __init__(self, name, album, artist):
        self.name = name
        self.album = album
        self.artist = artist


class AuthManager:
    def __init__(self, redirect_uri):
        self.cid = os.getenv('CLIENT_ID')
        self.redirect_uri = redirect_uri
        self.scopes = "playlist-read-private+playlist-read-collaborative+user-library-read"

    def create_auth_request(self):
        request = "https://accounts.spotify.com/authorize?client_id=" + self.cid + "&response_type=code&scope=" + self.scopes + "&redirect_uri=" + self.redirect_uri

        return request