import os
import spotipy
import requests
import base64
import time
import threading

import timer

from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
from dotenv import load_dotenv


class Client:
    def __init__(self):
        load_dotenv()
        self.cid = os.getenv('CLIENT_ID')
        self.secret = os.getenv('SECRET_ID')
        self.client_credentials_manager = SpotifyClientCredentials(client_id=self.cid, client_secret=self.secret)
        self.sp = spotipy.Spotify(client_credentials_manager = self.client_credentials_manager)

    def find(self, song_name):
        song = self.sp.search(q=song_name, type='track', limit=1)
        name = song['tracks']['items'][0]['name']
        album = song['tracks']['items'][0]['album']['name']
        artist = song['tracks']['items'][0]['artists'][0]['name']

        return name, album, artist

    def name_to_query(self, name, artist):
        modified_name = name.replace(' ', '+')
        modified_artist = artist.replace(' ', '+')
        search_query = 'https://www.youtube.com/results?search_query=' + modified_name + '+' + modified_artist

        return search_query

    def get_user_profile(self, access_token):
        url = 'https://api.spotify.com/v1/me'
        headers = {'Authorization': f'Bearer {access_token}',
                   'Content-type': 'application/x-www-form-urlencoded'}
        
        response = requests.get(url, headers=headers)

        return response

    def get_current_user_playlists(self, access_token, user_id):
        url = 'https://api.spotify.com/v1'

        headers = {'Authorization': access_token}
        payload = {'user_id': user_id}

        response = requests.get(url, params=payload, headers=headers)

        return response

    def get_user_playlists(self, access_token):
        url = 'https://api.spotify.com/v1/me/playlists'

        headers = {'Authorization': f'Bearer {access_token}'}

        response = requests.get(url, headers=headers)

        return response

    def get_playlist(self, access_token, playlist_id):
        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'

        headers = {'Authorization': f'Bearer {access_token}'}
        payload = {'market': 'CZ'}

        response = requests.get(url, params=payload, headers=headers)

        return response

    def playlist_exists(self, user_playlists, playlist_name):
        playlist_info = {}
        playlist_exists = False
        for item in user_playlists['items']:
            if item['name'].lower() == playlist_name:
                playlist_info['id'] = item['id']
                playlist_info['name'] = item['name']
                playlist_exists = True
                return playlist_info
            else:
                continue

        if not playlist_exists:
            return None

    def create_playlist(self, playlist_name, items):
        playlist = Playlist(playlist_name)

        for item in items['items']:
            track_name = item['track']['name']
            track_album = item['track']['album']['name']
            track_artists = item['track']['album']['artists'][0]['name']

            song = Song(track_name, track_album, track_artists)
            playlist.add_song(song)

        return playlist


class Song:
    def __init__(self, name, album, artist):
        self.name = name
        self.album = album
        self.artist = artist


class Playlist:
    def __init__(self, name):
        self.name = name
        self.items = []
    
    def add_song(self, song):
        self.items.append(song)

class AuthManager:
    def __init__(self, redirect_uri):
        self.cid = os.getenv('CLIENT_ID')
        self.secret = os.getenv('SECRET_ID')
        self.redirect_uri = redirect_uri
        self.scopes = 'user-read-email+user-read-private+playlist-read-private+playlist-read-collaborative'

    def create_auth_request(self):
        request = 'https://accounts.spotify.com/authorize?client_id=' + self.cid + '&response_type=code&scope=' + self.scopes + '&redirect_uri=' + self.redirect_uri

        return request

    def get_tokens(self, code):
        self.code = code
        auth_str = bytes(f'{self.cid}:{self.secret}', 'utf-8')
        b64_auth_str = base64.b64encode(auth_str).decode('utf-8')

        url = 'https://accounts.spotify.com/api/token'

        payload = {'grant_type': 'authorization_code',
                   'code': self.code,
                   'redirect_uri': self.redirect_uri}
        
        headers = {'Authorization': 'Basic {}'.format(b64_auth_str),
                   'Content-type': 'application/x-www-form-urlencoded'}

        response = requests.post(url, params=payload, headers=headers)
        
        return response


class TokenRefresher:
    def __init__(self):
        self.cid = os.getenv('CLIENT_ID')
        self.secret = os.getenv('SECRET_ID')

    def get_new_token(self, refresh_token):
        auth_str = bytes('{}:{}'.format(self.cid, self.secret), 'utf-8')
        b64_auth_str = base64.b64encode(auth_str).decode('utf-8')
        
        url = 'application/x-www-form-urlencoded'

        payload = {'grant_type': 'refresh_token',
                   'refresh_token': refresh_token}

        headers = {'Authorization': 'Basic {}'.format(b64_auth_str),
                   'Content-type': 'application/x-www-form-urlencoded'}

        response = requests.post(url, params=payload, headers=headers)

        return response

    def start_refresh_cycle(self, token_expiration, user):
        refresh_cycle = threading.Thread(target=self.__keep_token_updated, args=(token_expiration, user,))
        refresh_cycle.daemon = True
        refresh_cycle.start()

    def __keep_token_updated(self, token_expiration, user):
        refresh_token = user.refresh_token
        expired = False
        exp_timer = timer.Timer()
        exp_timer.start()

        while not expired:
            if token_expiration - 120 > exp_timer.elapsed_time():
                time.sleep(1)
            else:
                access_token = self.get_new_token(refresh_token)
                token_expiration = access_token['expires_in']

                user.access_token = access_token

                self.start_refresh_cycle(token_expiration, user)
                expired = True


class AudioFinder:
    def find_url(self, song):
        searched_expression = f'{song.artist} {song.name}'
        video_info = VideosSearch(searched_expression, limit=1)
        video_url = video_info.result()['result'][0]['link']
        return video_url