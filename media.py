from flask import request, redirect, url_for, Response, Blueprint
from urllib import parse
import requests
import socket
import base64
from subprocess import run
import json

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import logging
import random

import config_reader as cfg

app_media = Blueprint('app_media', __name__, template_folder='templates')
log = logging.getLogger('server.sub')
log.setLevel(logging.INFO)

# URLs
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)
SPOTIFY_PLAYER_URL = SPOTIFY_API_URL+"/me/player"
SPOTIFY_PLAYABLE_URI = cfg.get_spotify_playable_uri()
READ_ERRORS_OUT_LOUD = cfg.get_read_errors_out_loud()

SPOTIFY_DEVICE_ID =  cfg.get_spotify_device_id()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

HOSTNAME = get_local_ip()
PORT = 3141
THIS_SERVER_ADDRESS = "http://" + HOSTNAME + ":" + str(PORT)


SPOTIFY_REDIRECT_URI = THIS_SERVER_ADDRESS + "/authorize_spotify"

playlist_id = '7jirtU9sm2aEe5DYK8n6Id' # Dave/Easy Wakeup
#playlist_id = '5crU6AclXGahkiVpvIcbZQ' # Janek/raspi-alarm-clock

# from playlists import playlists #TODO

# TODO: In context of /login, maybe rename to refresh auth
@app_media.route("/request_spotify_authorization")
def request_spotify_authorization(code=None):
    if code != None:
        # Ask for a refresh token and access token using code received from Spotify in /login
        # (Step 2 of 'Authorization Code Flow')
        # https://developer.spotify.com/documentation/general/guides/authorization-guide/
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": SPOTIFY_REDIRECT_URI,
        }
    else:
        # Ask for an access token using a refresh token
        # (Step 4 of 'Authorization Code Flow')
        # https://developer.spotify.com/documentation/general/guides/authorization-guide/
        data = {
            "grant_type": "refresh_token",
            "refresh_token": cfg.get_spotify_refresh_token()
        }

    client_id = cfg.get_spotify_client_id()
    client_secret = cfg.get_spotify_client_secret()
    
    auth_str = '{}:{}'.format(client_id, client_secret)
    b64_auth_str = base64.urlsafe_b64encode(auth_str.encode()).decode()
    headers = {"Authorization": "Basic {}".format(b64_auth_str)}
    response = requests.post(SPOTIFY_TOKEN_URL, data=data, headers=headers)
    error = handle_and_return_possible_error_message_in_api_response(response)
    response_data = response.json()
    if error:
        return error
    elif "access_token" in response_data:
        access_token = response_data["access_token"]
        file = open("access_token.txt", "w")
        file.write(access_token)
        file.close()
        refresh_token_received = "refresh_token" in response_data
        if refresh_token_received:
            refresh_token = response_data["refresh_token"]
            cfg.set_spotify_refresh_token(refresh_token)
        message = "Retrieved and saved access token" + (" and refresh token" if refresh_token_received else "")
        log.info(message)
        return message
    else:
        return "Unknown problem with response to request_spotify_authorization"

def handle_and_return_possible_error_message_in_api_response(response):
    if response.ok:
        return
    response_data = response.json()
    
    if "error" in response_data:
        if "error_description" in response_data:
            error_message =  response_data["error_description"]
        elif "message" in response_data["error"]:
            error_message = response_data["error"]["message"] 
        log.info(error_message)
        if READ_ERRORS_OUT_LOUD:
            say("Error: " + error_message)
        return error_message
    
@app_media.route("/authorize_spotify")
def authorize_spotify():
    # XXX: Handle erroneous response 
    # (https://developer.spotify.com/documentation/general/guides/authorization-guide/)
    code = request.args.get('code')
    status_message = request_spotify_authorization(code=code)
    return status_message 
        
@app_media.route("/login")
def login():
    scopes = "user-read-playback-state user-modify-playback-state"
    login_url = SPOTIFY_AUTH_URL + '?response_type=code' + '&client_id=' + cfg.get_spotify_client_id() + '&scope=' + parse.quote(scopes) + '&redirect_uri=' + parse.quote(SPOTIFY_REDIRECT_URI)
    return redirect(login_url, code=302)

def access_token_from_file():
    file = open("access_token.txt","r")
    access_token = file.read()
    file.close()
    return access_token

@app_media.route('/devices', methods=['GET'])
def devices():
    response = spotify_request("devices", http_method="GET")
    return response.text

def spotify_request(endpoint, http_method="PUT",  data=None, force_device=False, token=None, url_params={}, retries_attempted=0):
    log.info("Request to endpoint '/" + endpoint + "' attempted")

    if token is None:
        token = access_token_from_file()
    if force_device:
        url_params["device_id"] = SPOTIFY_DEVICE_ID

    url = SPOTIFY_PLAYER_URL + "/" + endpoint
    headers = {'Authorization': 'Bearer {}'.format(token)} 

    if http_method == "PUT":
        response = requests.put(url, data=data, headers=headers, params=url_params)
    elif http_method == "GET":
        response = requests.get(url, data=data, headers=headers, params=url_params)

    log.info("Request to " + str(url) + " \n Response = " + str(response.status_code) + " " + response.text)

    if response.status_code == 401:
        # If the access token is expired, get a new one and retry
        token = request_spotify_authorization()
        headers = {'Authorization': 'Bearer {}'.format(token)}
        response = requests.put(url, data=data, headers=headers, params=url_params)
        # Retry request
        if retries_attempted < 1:
            response = spotify_request(endpoint, http_method, data, force_device, token, url_params, retries_attempted+1)
    else: 
        handle_and_return_possible_error_message_in_api_response(response)
    return response

@app_media.route("/spotipause")
def spotipause():
    log.info('Pausing spotify')
    response = pause()
    return "Pause request sent to Spotify. Response: " + str(response.status_code) + " " + response.text

@app_media.route("/spotiplay")
def spotiplay():
    log.info('Playing spotify')
    radiostop()
    response = play_random(spotify_uri="spotify:playlist:" + playlist_id)
    return "Play request sent to Spotify. Response: " + str(response.status_code) +  " " + response.text



#Todo use spotipy to set spotify playback to shuffle 
def play_random(spotify_uri=None): 

    # set up Spotify API credentials
    client_id = cfg.get_spotify_client_id()
    client_secret = cfg.get_spotify_client_secret()
    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # get number of tracks in playlist
    playlist = sp.playlist(playlist_id)
    num_tracks = playlist['tracks']['total']

    # call play with random track number
    random_track_number = random.randint(0, num_tracks)
    log.info("Playing #" + str(random_track_number) + " from: " + playlist['name'] )
    return play(spotify_uri=spotify_uri, song_number=random_track_number)

def play(spotify_uri=None, song_number=0): 
    global currently_playing
    data = ''
    if spotify_uri != None:
        data = '{"context_uri":"' + spotify_uri + '","offset":{"position":' + str(song_number) + '},"position_ms":0}'
    response = spotify_request("play", force_device=True, data=data)
    if response.ok:
        currently_playing = True
    if response.status_code == 404:
        # Hardcoded device not found
        try: 
            radioplay()
            log.info('Spotify device not found, playing radio')
        except:
            log.info("Spotify device not found and failed to play radio")
            
    return response

def pause():
    global currently_playing
    response = spotify_request("pause")
    if response.ok:
        currently_playing = False
    return response

def playpause():
    global currently_playing
    if currently_playing:
        pause()
    else:
        play()

@app_media.route("/stop")
def stop():
    radiostop()
    spotipause()
    return "Playback stopped"

@app_media.route("/radioplay")
def radioplay():
    log.info('Starting radio')
    run(["mpc", "play"])
    return "Radio started"

@app_media.route("/radiostop")
def radiostop():
    log.info('Stopping radio')
    run(["mpc", "stop"])
    return "Radio stopped"

@app_media.route("/radionext")
def radionext():
    log.info("Playing next radio station")
    run(["mpc", "next"])
    return "Playing next radio station"

@app_media.route("/radioprev")
def radioprev():
    log.info("Playing prev radio station")
    run(["mpc", "prev"])
    return "Playing prev radio station"

def set_volume_spotify(new_volume):
    url_params={}
    url_params["volume_percent"] = int(new_volume)
    response = spotify_request("volume", url_params=url_params)
    return response.text