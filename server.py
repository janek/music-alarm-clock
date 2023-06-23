import json
import time
import threading
from flask import Flask, request, redirect, url_for, Response
from urllib import parse
import requests
from subprocess import run
import subprocess
import base64
from crontab import CronTab
import config_reader as cfg
import os
import socket
import logging
# from playlists import playlists #TODO

app = Flask(__name__)

# URLs
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)
SPOTIFY_PLAYER_URL = SPOTIFY_API_URL+"/me/player"
SPOTIFY_PLAYABLE_URI = cfg.get_spotify_playable_uri()
READ_ERRORS_OUT_LOUD = cfg.get_read_errors_out_loud()

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

# App's global constants
SYSTEM_USER = os.environ.get('USER')
SPOTIFY_DEVICE_ID =  cfg.get_spotify_device_id()
ALARM_ANNOTATION_TAG = "SPOTIFY ALARM"  # Identifies our lines in crontab
currently_playing = False



# TODO: In context of /login, maybe rename to refresh auth
@app.route("/request_spotify_authorization")
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
        app.logger.info(message)
        return message
    else:
        return "Unknown problem with response to request_spotify_authorization"

@app.route("/authorize_spotify")
def authorize_spotify():
    # XXX: Handle erroneous response 
    # (https://developer.spotify.com/documentation/general/guides/authorization-guide/)
    code = request.args.get('code')
    status_message = request_spotify_authorization(code=code)
    return status_message 
        
@app.route("/login")
def login():
    scopes = "user-read-playback-state user-modify-playback-state"
    login_url = SPOTIFY_AUTH_URL + '?response_type=code' + '&client_id=' + cfg.get_spotify_client_id() + '&scope=' + parse.quote(scopes) + '&redirect_uri=' + parse.quote(SPOTIFY_REDIRECT_URI)
    return redirect(login_url, code=302)

@app.route("/spotialarm")
def spotialarm():
   app.logger.info('Starting spotify alarm') 
   start_fading_volume_in_thread()
   spotiplay()
   return "Spotify alarm started"

@app.route("/spotipause")
def spotipause():
    app.logger.info('Pausing spotify')
    response = pause()
    return "Pause request sent to Spotify. Response: " + str(response.status_code) + " " + response.text


@app.route("/spotiplay")
def spotiplay():
    app.logger.info('Playing spotify')
    radiostop()
    response = play(spotify_uri="spotify:playlist:5crU6AclXGahkiVpvIcbZQ")
    return "Play request sent to Spotify. Response: " + str(response.status_code) +  " " + response.text

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
            app.logger.info('Spotify device not found, playing radio')
        except:
            app.logger.info("Spotify device not found and failed to play radio")
            
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

def start_fading_volume_in_thread(goal_volume=100, fade_duration_mins=1):
    # start fade_volume in a new thread
    fade_thread = threading.Thread(target=fade_volume, args=(goal_volume, fade_duration_mins))
    fade_thread.start()

def fade_volume(goal_volume=70, fade_duration_mins=1):
    set_volume(0)
    fade_duration_secs = fade_duration_mins * 60
    sleep_time = fade_duration_secs / goal_volume
    for i in range(0, goal_volume):
        set_volume(i)
        time.sleep(sleep_time)

@app.route("/volume")
def volume():
    new_volume = request.args.get('volume')
    set_volume(new_volume)
    return "Volume set to " + str(new_volume) if new_volume is not None else "Volume not set"

def set_volume(new_volume):
    run(["amixer", "set", "Master", str(new_volume) + "%"])

def spotify_request(endpoint, http_method="PUT",  data=None, force_device=False, token=None, url_params={}, retries_attempted=0):
    app.logger.info("Request to endpoint '/" + endpoint + "' attempted")
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

    app.logger.debug("Request to " + str(url) + " \n Response = " + str(response.status_code) + " " + response.text)

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

def handle_and_return_possible_error_message_in_api_response(response):
    if response.ok:
        return
    response_data = response.json()
    
    if "error" in response_data:
        if "error_description" in response_data:
            error_message =  response_data["error_description"]
        elif "message" in response_data["error"]:
            error_message = response_data["error"]["message"] 
        app.logger.info(error_message)
        if READ_ERRORS_OUT_LOUD:
            say("Error: " + error_message)
        return error_message

def access_token_from_file():
    file = open("access_token.txt","r")
    access_token = file.read()
    file.close()
    return access_token

def say(something):
    run(["espeak", something], stdout=subprocess.DEVNULL)

@app.route("/stop")
def stop():
    radiostop()
    spotipause()
    return "Playback stopped"

@app.route("/radioplay")
def radioplay():
    app.logger.info('Starting radio')
    run(["mpc", "play"])
    return "Radio started"

@app.route("/radioalarm")
def radioalarm():
    app.logger.info('Starting radio alarm')
    start_fading_volume_in_thread()
    radioplay()
    return "Radio alarm started"

@app.route("/radiostop")
def radiostop():
    app.logger.info('Stopping radio')
    run(["mpc", "stop"])
    return "Radio stopped"

@app.route("/radionext")
def radionext():
    app.logger.info("Playing next radio station")
    run(["mpc", "next"])
    return "Playing next radio station"

@app.route("/radioprev")
def radioprev():
    app.logger.info("Playing prev radio station")
    run(["mpc", "prev"])
    return "Playing prev radio station"

@app.route('/cronsave', methods=['POST'])
def cronsave():
    minutes = request.json['minutes']
    hours = request.json['hours']
    music_mode = request.json['mode']
    if music_mode == "luz" or music_mode == "radio":
        command = "curl " + THIS_SERVER_ADDRESS + "/radioalarm"
    else:
        command = "curl " + THIS_SERVER_ADDRESS + "/spotialarm"
    cron_raspi = CronTab(user=SYSTEM_USER)
    cron_raspi.remove_all(comment=ALARM_ANNOTATION_TAG)
    job = cron_raspi.new(command=command, comment=ALARM_ANNOTATION_TAG)
    job.minute.on(minutes)
    job.hour.on(hours)
    cron_raspi.write()
    app.logger.info("Alarm set to " + str(hours) + ":" + str(minutes))
    return "Alarm saved!"

@app.route('/devices', methods=['GET'])
def devices():
    response = spotify_request("devices", http_method="GET")
    return response.text

@app.route('/cronclean', methods=['GET'])
def cronclean():
    cron_raspi = CronTab(user=SYSTEM_USER)
    cron_raspi.remove_all(comment=ALARM_ANNOTATION_TAG)
    cron_raspi.write()
    return "All alarms cleared."

@app.route('/areyourunning', methods=['GET'])
def areyourunning():
    message = "Alarm-clock server is running."
    say(message)
    return message

if __name__ == '__main__':
    app.logger.setLevel(logging.INFO)
    # TODO eventually deploy ?!
    app.run(debug=True, port=PORT, host='0.0.0.0')

