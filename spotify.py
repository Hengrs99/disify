import os
import spotipy
import requests
import base64
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

    def get_user_profile(self, access_token):
        url = "https://api.spotify.com/v1/me"
        headers = {"Authorization": f"Bearer {access_token}",
                   "Content-type": "application/x-www-form-urlencoded"}
        
        response = requests.get(url, headers=headers)

        return response

    def get_user_playlists(self, access_token, user_id):
        url = "https://api.spotify.com/v1"

        headers = {"Authorization": access_token}
        payload = {"user_id": user_id}

        response = requests.get(url, params=payload, headers=headers)

        return response

class Song:
    def __init__(self, name, album, artist):
        self.name = name
        self.album = album
        self.artist = artist


class AuthManager:
    def __init__(self, redirect_uri):
        self.cid = os.getenv('CLIENT_ID')
        self.secret = os.getenv('SECRET_ID')
        self.redirect_uri = redirect_uri
        self.scopes = "user-read-email+user-read-private+playlist-read-private+playlist-read-collaborative"

    def create_auth_request(self):
        request = "https://accounts.spotify.com/authorize?client_id=" + self.cid + "&response_type=code&scope=" + self.scopes + "&redirect_uri=" + self.redirect_uri

        return request

    def get_tokens(self, code):
        self.code = code
        auth_str = bytes('{}:{}'.format(self.cid, self.secret), 'utf-8')
        b64_auth_str = base64.b64encode(auth_str).decode('utf-8')

        url = "https://accounts.spotify.com/api/token"

        payload = {"grant_type": "authorization_code",
                   "code": self.code,
                   "redirect_uri": self.redirect_uri}
        
        headers = {"Authorization": "Basic {}".format(b64_auth_str),
                   "Content-type": "application/x-www-form-urlencoded"}

        response = requests.post(url, params=payload, headers=headers)
        
        return response

    def get_new_token(self, refresh_token):
        auth_str = bytes('{}:{}'.format(self.cid, self.secret), 'utf-8')
        b64_auth_str = base64.b64encode(auth_str).decode('utf-8')
        
        url = "application/x-www-form-urlencoded"

        payload = {"grant_type": "refresh_token",
                   "refresh_token": refresh_token}

        headers = {"Authorization": "Basic {}".format(b64_auth_str),
                   "Content-type": "application/x-www-form-urlencoded"}

        response = requests.post(url, params=payload, headers=headers)

        return response