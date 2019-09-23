import json
from flask import Flask, request
import requests
from subprocess import run
import base64
from crontab import CronTab
import config_reader as cfg
# from playlists import playlists #TODO


app = Flask(__name__)

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)
SPOTIFY_PLAYER_URL = SPOTIFY_API_URL+"/me/player"

# App's global constants
SYSTEM_USER = "pi"  # janek
PI_DEVICE_ID = "638c4613fba455726772c486cba9acc0775f49e"
ALARM_ANNOTATION_TAG = "SPOTI-ALARM"  # Identifies our lines in crontab
RADIO_STREAM_URL = "http://radioluz.pwr.edu.pl:8000/luzlofi.ogg"
HOSTNAME = "0.0.0.0"
PORT = 3141
ADDRESS = HOSTNAME + ":" + str(PORT)

# Global state variables
currently_playing = False


@app.route("/spotiauth")
def spotiauth():
    # Ask for a new access token, using the refresh token,
    # CLIENT_ID and CLIENT_SECRET. Save it to a file.
    data = {
        "grant_type": "refresh_token",
        "refresh_token": cfg.get_spotify_refresh_token()
    }

    client_id = cfg.get_spotify_client_id()
    client_secret = cfg.get_spotify_client_secret()
    auth_str = '{}:{}'.format(client_id, client_secret)
    b64_auth_str = base64.urlsafe_b64encode(auth_str.encode()).decode()
    headers = {"Authorization": "Basic {}".format(b64_auth_str)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=data, headers=headers)
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]

    file = open("access_token.txt", "w")
    file.write(access_token)
    file.close()

    return access_token


@app.route("/spotipause")
def spotipause():
    pause()
    return "Attempted pause"


@app.route("/spotiplay")
def spotiplay():
    response = play(spotify_uri="spotify:album:5uiLjgmdPV4dgamvmC64Oq")
    return "SPOTIPLAY, RESPONSE: \n" + response.text


def play(spotify_uri=None, song_number=0, retries_attempted=0): 
    # XXX: naming problem between this and spotiplay
    global currently_playing
    data = ''
    if spotify_uri != None:
        data = '{"context_uri":"' + spotify_uri + '","offset":{"position":' + str(song_number) + '},"position_ms":0}'
    response = spotify_request("play", data=data)
    if response.status_code == 204:
        currently_playing = True
    return response


def pause():
    global currently_playing
    response = spotify_request("pause")
    if response.status_code == 204:
        currently_playing = False
    return response


def playpause():
    global currently_playing
    if currently_playing:
        pause()
    else:
        play()


def set_volume(new_volume):
    url_params = {"volume_percent":str((new_volume+1)*10)}
    response = spotify_request("volume", url_params=url_params)
    return response


def spotify_request(endpoint, data=None, force_device=False, token=None, url_params=[]):
    if token is None:
        token = access_token_from_file()
    if force_device:
        url_params["device_id"] = PI_DEVICE_ID
    url = SPOTIFY_PLAYER_URL + "/" + endpoint
    headers = {'Authorization': 'Bearer {}'.format(token)} 
    response = requests.put(url, data=data, headers=headers, params=url_params)

    if response.status_code == 401:
        # If token is expired, get a new one and retry
        token = spotiauth()
        headers = {'Authorization': 'Bearer {}'.format(token)}
        response = request.put(url, data=data, headers=headers, params=url_params)

    return response


def access_token_from_file():
    file = open("access_token.txt","r")
    access_token = file.read()
    file.close()
    return access_token


@app.route("/radioplay")
def radioplay():
    run(["omxplayer", RADIO_STREAM_URL])
    return "LUZ"


@app.route('/cronsave', methods=['POST'])
def cronsave():
    minutes = request.json['minutes']
    hours = request.json['hours']
    music_mode = request.json['mode']
    if music_mode == "luz":
        command = "curl " + ADDRESS + "/radioplay"
    else:
        command = "curl " + ADDRESS + "/spotiauth && curl " + ADDRESS + "/spotiplay"
    cron_raspi = CronTab(user=SYSTEM_USER)
    cron_raspi.remove_all(comment=ALARM_ANNOTATION_TAG)
    job = cron_raspi.new(command=command, comment=ALARM_ANNOTATION_TAG)
    job.minute.on(minutes)
    job.hour.on(hours)
    cron_raspi.write()
    return "OK"


@app.route('/cronclean', methods=['GET'])
def cronclean():
    cron_raspi = CronTab(user=SYSTEM_USER)
    cron_raspi.remove_all(comment=ALARM_ANNOTATION_TAG)
    cron_raspi.write()
    return "CLEANED"


@app.route('/areyourunning', methods=['GET'])
def areyourunning():
    return "YES"


if __name__ == '__main__':
    app.run(debug=True, port=PORT, host='0.0.0.0')
