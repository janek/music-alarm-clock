import time
import socket
import threading
from flask import Flask, request, redirect, render_template
import datetime
from urllib import parse
import requests
from subprocess import run
import re
from subprocess import check_output
import subprocess
import base64
from crontab import CronTab
import config_reader as cfg
import os
import socket
import logging

import math

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import random

# from playlists import playlists #TODO

app = Flask(__name__)

# URLs
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)
SPOTIFY_PLAYER_URL = SPOTIFY_API_URL + "/me/player"
SPOTIFY_PLAYABLE_URI = cfg.get_spotify_playable_uri()
READ_ERRORS_OUT_LOUD = cfg.get_read_errors_out_loud()

# playlist_id = "7jirtU9sm2aEe5DYK8n6Id"  # Dave/Easy Wakeup
playlist_id = '5crU6AclXGahkiVpvIcbZQ' # Janek/raspi-alarm-clock


def get_local_hostname():
    try:
        hostname = socket.gethostname()
    except:
        hostname = "localhost"
    return hostname


HOSTNAME = get_local_hostname()
PORT = 3141
THIS_SERVER_ADDRESS = "http://" + HOSTNAME + ":" + str(PORT)
SPOTIFY_REDIRECT_URI = THIS_SERVER_ADDRESS + "/authorize_spotify"

# App's global constants
SYSTEM_USER = os.environ.get("USER")
SPOTIFY_DEVICE_ID = cfg.get_spotify_device_id()
ALARM_ANNOTATION_TAG = "SPOTIFY ALARM"  # Identifies our lines in crontab
currently_playing = False
fade_minutes = 2

g_balance = 0

# set up initial alarm time
alarm_time = datetime.time(hour=8, minute=0)
alarm_active = False


def render():
    return render_template(
        "index.html", alarm_time=alarm_time, alarm_active=alarm_active
    )


# define routes
@app.route("/")
def index():
    return render()


@app.route("/set_alarm_active", methods=["POST"])
def set_alarm_active():
    global alarm_active
    global alarm_time
    alarm_active = request.json["alarm_active"]

    if not alarm_active:
        cronclean()
    else:
        save_alarm(alarm_time.hour, alarm_time.minute)

    return render()


@app.route("/set_alarm", methods=["POST"])
def set_alarm():
    global alarm_active

    alarm_active = True

    global alarm_time
    hour = int(request.form["hour"])
    minute = int(request.form["minute"])
    # print alarm
    print("Alarm set to " + str(hour) + ":" + str(minute))

    alarm_time = datetime.time(hour=hour, minute=minute)

    save_alarm(hour, minute)

    return render()


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
            "refresh_token": cfg.get_spotify_refresh_token(),
        }

    client_id = cfg.get_spotify_client_id()
    client_secret = cfg.get_spotify_client_secret()

    auth_str = "{}:{}".format(client_id, client_secret)
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
        message = "Retrieved and saved access token" + (
            " and refresh token" if refresh_token_received else ""
        )
        app.logger.info(message)
        return message
    else:
        return "Unknown problem with response to request_spotify_authorization"


@app.route("/authorize_spotify")
def authorize_spotify():
    # XXX: Handle erroneous response
    # (https://developer.spotify.com/documentation/general/guides/authorization-guide/)
    code = request.args.get("code")
    status_message = request_spotify_authorization(code=code)
    return status_message


@app.route("/login")
def login():
    scopes = "user-read-playback-state user-modify-playback-state"
    login_url = (
        SPOTIFY_AUTH_URL
        + "?response_type=code"
        + "&client_id="
        + cfg.get_spotify_client_id()
        + "&scope="
        + parse.quote(scopes)
        + "&redirect_uri="
        + parse.quote(SPOTIFY_REDIRECT_URI)
    )
    return redirect(login_url, code=302)


def homeassistant_triggerWebhook(webhook_name):
    url = "http://" + HOSTNAME + ":" + str(8123) + "/api/webhook/" + webhook_name
    try:
        response = requests.get(url)
        if response.status_code == 405:
            result = "Triggered Webhook"
            response = requests.put(url)
        else:
            result = (
                "Did not find Webhook (create an automation in homeassistant first)"
            )
    except requests.ConnectionError:
        result = "Connection error. Check if Home Assistant is running and network connectivity is fine."

    result = result + ": " + url
    logging.info(result)
    return result


@app.route("/spotialarm")
def spotialarm():
    app.logger.info("Starting spotify alarm")
    global fade_minutes
    start_fade_volume_in(goal_volume=70, fade_duration_mins=fade_minutes)

    try:
        spotiplay()
        homeassistant_triggerWebhook("wakeup_alarm_triggered")
        return "Spotify alarm started"
    except:
        print("spotiplay() did not work...")
        return radioalarm()


@app.route("/spotipause")
def spotipause():
    app.logger.info("Pausing spotify")
    response = pause()
    return (
        "Pause request sent to Spotify. Response: "
        + str(response.status_code)
        + " "
        + response.text
    )


@app.route("/spotiplay")
def spotiplay():
    app.logger.info("Playing spotify")
    radiostop()
    response = play_random(spotify_uri="spotify:playlist:" + playlist_id)
    return (
        "Play request sent to Spotify. Response: "
        + str(response.status_code)
        + " "
        + response.text
    )


# Todo use spotipy to set spotify playback to shuffle
def play_random(spotify_uri=None):
    # set up Spotify API credentials
    client_id = cfg.get_spotify_client_id()
    client_secret = cfg.get_spotify_client_secret()
    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # get number of tracks in playlist
    playlist = sp.playlist(playlist_id)
    num_tracks = playlist["tracks"]["total"]

    # call play with random track number
    random_track_number = random.randint(0, num_tracks)
    app.logger.info(
        "Playing #" + str(random_track_number) + " from: " + playlist["name"]
    )
    return play(spotify_uri=spotify_uri, song_number=random_track_number)


def play(spotify_uri=None, song_number=0):
    global currently_playing
    data = ""
    if spotify_uri != None:
        data = (
            '{"context_uri":"'
            + spotify_uri
            + '","offset":{"position":'
            + str(song_number)
            + '},"position_ms":0}'
        )
    response = spotify_request("play", force_device=True, data=data)
    if response.ok:
        currently_playing = True
    if response.status_code == 404:
        # Hardcoded device not found
        try:
            radioplay()
            app.logger.info("Spotify device not found, playing radio")
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


def start_fade_volume_in(goal_volume=70, fade_duration_mins=1.0):
    # start fade_volume_in in a new thread
    fade_thread = threading.Thread(
        target=fade_volume_in, args=(goal_volume, fade_duration_mins)
    )
    fade_thread.start()


def fade_volume_in(goal_volume=70, fade_duration_mins=1):
    set_volume(0)
    fade_duration_secs = fade_duration_mins * 60
    sleep_time = fade_duration_secs / goal_volume
    for i in range(0, goal_volume):
        set_volume(i / 100)
        time.sleep(sleep_time)


def start_fade_volume_out(fade_duration_mins=1.0):
    # start fade_volume_in in a new thread
    try:
        fade_thread = threading.Thread(
            target=fade_volume_out, args=(fade_duration_mins,)
        )
        fade_thread.start()
    except:
        app.logger.info("Failed to start fade_volume_out thread")


def fade_volume_out(fade_duration_mins=1):
    try:
        fade_duration_secs = fade_duration_mins * 60
        current_volume = get_volume()
        sleep_time = fade_duration_secs / current_volume
        for i in range(current_volume, 0):
            set_volume(i)
            time.sleep(sleep_time)
    except:
        app.logger.info("Failed to fade_volume_out")
        # print trace with logger
        app.logger.exception("message")

    radiostop()
    spotipause()


@app.route("/volume")
def volume():
    new_volume = float(request.args.get("volume")) / 100.0

    b = request.args.get("balance")
    if b is not None:
        set_volume(new_volume, float(b))
    else:
        set_volume(new_volume)

    return (
        "Volume set to " + str(new_volume)
        if new_volume is not None
        else "Volume not set"
    )


def get_volume():
    output = check_output(["amixer", "get", "Master"])
    match = re.search(r"\[(\d+)%\]", output.decode())
    if match:
        return int(match.group(1))
    else:
        return None


def set_volume(volume, balance=-1):
    global g_balance
    # volume  is a float from 0 -1
    volume = max(min(float(volume), 1), 0)

    if balance != -1:
        # balance is a float ranging from -1 (full left) to 1 (full right)
        # clamp balance to range [-1, 1] to avoid errors
        g_balance = max(min(float(balance), 1), -1)

    # calculate left and right channel volumes
    # the 'sqrt' function ensures power (not amplitude) balance
    left = math.sqrt((g_balance - 1) / -2) * 100
    right = math.sqrt((g_balance + 1) / 2) * 100

    left *= volume
    right *= volume

    # convert to percentages and make sure volumes are within [0, 100]
    left = min(max(left, 0), 100)
    right = min(max(right, 0), 100)

    # set volumes
    command = f"amixer sset 'Master' {left}%,{right}%"
    os.system(command)
    app.logger.info(f"Volume set {volume}, {balance} =>({left}% left, {right}% right)")


def spotify_request(
    endpoint,
    http_method="PUT",
    data=None,
    force_device=False,
    token=None,
    url_params={},
    retries_attempted=0,
):
    app.logger.info("Request to endpoint '/" + endpoint + "' attempted")
    if token is None:
        token = access_token_from_file()
    if force_device:
        url_params["device_id"] = SPOTIFY_DEVICE_ID
    url = SPOTIFY_PLAYER_URL + "/" + endpoint
    headers = {"Authorization": "Bearer {}".format(token)}

    if http_method == "PUT":
        response = requests.put(url, data=data, headers=headers, params=url_params)
    elif http_method == "GET":
        response = requests.get(url, data=data, headers=headers, params=url_params)

    app.logger.info(
        "Request to "
        + str(url)
        + " \n Response = "
        + str(response.status_code)
        + " "
        + response.text
    )

    if response.status_code == 401:
        # If the access token is expired, get a new one and retry
        token = request_spotify_authorization()
        headers = {"Authorization": "Bearer {}".format(token)}
        response = requests.put(url, data=data, headers=headers, params=url_params)
        # Retry request
        if retries_attempted < 1:
            response = spotify_request(
                endpoint,
                http_method,
                data,
                force_device,
                token,
                url_params,
                retries_attempted + 1,
            )
    else:
        handle_and_return_possible_error_message_in_api_response(response)
    return response


def handle_and_return_possible_error_message_in_api_response(response):
    if response.ok:
        return
    response_data = response.json()

    if "error" in response_data:
        if "error_description" in response_data:
            error_message = response_data["error_description"]
        elif "message" in response_data["error"]:
            error_message = response_data["error"]["message"]
        app.logger.info(error_message)
        if READ_ERRORS_OUT_LOUD:
            say("Error: " + error_message)
        return error_message

def access_token_from_file():
    with open("access_token.txt", "r") as f:
        access_token = f.read()
    return access_token

def say(something):
    run(["espeak", something], stdout=subprocess.DEVNULL)


@app.route("/stop")
def stop(fade_duration_mins=0):
    if fade_duration_mins > 0:
        start_fade_volume_out(fade_duration_mins)
        return "Fading out playback over " + str(fade_duration_mins) + " minutes"
    else:
        radiostop()
        spotipause()
        return "Playback stopped"


@app.route("/radioplay")
def radioplay():
    app.logger.info("Starting radio")
    run(["mpc", "play"])
    return "Radio started"


@app.route("/radioalarm")
def radioalarm():
    app.logger.info("Starting radio alarm")
    start_fade_volume_in(fade_duration_mins=fade_minutes)
    radioplay()
    homeassistant_triggerWebhook("wakeup_alarm_triggered")
    return "Radio alarm started"


@app.route("/radiostop")
def radiostop():
    app.logger.info("Stopping radio")
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


@app.route("/cronsave", methods=["POST"])
def cronsave():
    global fade_minutes

    if "fade_minutes" in request.json:
        fade_minutes = request.json["fade_minutes"]

    success = save_alarm(
        request.json["hours"], request.json["minutes"], music_mode=request.json["mode"]
    )

    return "Alarm saved" if success else "Alarm not saved"


@app.route("/cronclean", methods=["GET"])
def cronclean():
    cron_raspi = CronTab(user=SYSTEM_USER)
    cron_raspi.remove_all(comment=ALARM_ANNOTATION_TAG)
    cron_raspi.write()
    return "All alarms cleared."


def save_alarm(hours, minutes, music_mode="radio"):
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
    return True


@app.route("/devices", methods=["GET"])
def devices():
    response = spotify_request("devices", http_method="GET")
    return response.text


@app.route("/areyourunning", methods=["GET"])
def areyourunning():
    message = "Alarm-clock server is running."
    say(message)
    return message


if __name__ == "__main__":
    app.logger.setLevel(logging.INFO)
    app.logger.info("Starting \n\n \n\n server.py -> __main__ \n \n ")

    if SYSTEM_USER == None:
        SYSTEM_USER = "pi"

    # retrieve alarm_time from crontab
    cron = CronTab(user=SYSTEM_USER)

    for job in cron.find_comment(ALARM_ANNOTATION_TAG):
        try:
            hour, minute = job.hour.parts[0], job.minute.parts[0]
            alarm_time = datetime.time(hour=hour, minute=minute)
            app.logger.info("Found alarm in crontab: " + str(alarm_time))
            alarm_active = True
        except:
            app.logger.info("No alarm in crontab!")
            alarm_active = False

    # radioalarm()
    # TODO eventually deploy ?!
    app.run(debug=True, port=PORT, host="0.0.0.0")
