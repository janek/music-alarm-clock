import json
from flask import Flask, request
from subprocess import run
import requests
import base64
from crontab import CronTab

app = Flask(__name__)

#  Client Keys
CLIENT_ID = "7e1cc7ca19974c4ba5e904e5c20784ac"
CLIENT_SECRET = "7205a4e9e27f49b1b689e532a1bb5801"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)
SPOTIFY_PLAY_URL = SPOTIFY_API_BASE_URL+"/me/player/play"

# Server-side parameters
SYSTEM_USER = "pi" # janek
REF_TOKEN = "AQD3owby0pWQOqv1G2WIXGrDiV-EQ5doPORTMPdes5YllKJ9Pu0QO2_EojrjfY4EOVPEN9YAH7Ln82_8bGj9gy8xDapcCRNy5U7qlNmzFwsU3wNdps69HF-VgPOre5EBdaSxBCOzWA"


# App's global variables
ALARM_ADNOTATION_TAG = "SPOTI-ALARM" # Identifies lines in crontab created by this program (and not other users/programs)
RADIO_STREAM_URL = "http://radioluz.pwr.edu.pl:8000/luzlofi.ogg" 


@app.route("/spotiauth")
def spotiauth():
    # Ask for a new access token, using the refresh token, CLIENT_ID and CLIENT_SECRET. Save it to a file.
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REF_TOKEN
    }

    auth_str = '{}:{}'.format(CLIENT_ID,CLIENT_SECRET)
    b64_auth_str = base64.urlsafe_b64encode(auth_str.encode()).decode()
    headers = {"Authorization": "Basic {}".format(b64_auth_str)} 
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=data, headers=headers)
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]

    file = open("access_token.txt","w") 
    file.write(access_token) 
    file.close() 

    return access_token

@app.route("/spotiplay")
def spotiplay():
    # Read the currently saved token. Use it to connect to the spotify /me/player/play endpoint and start playing music 
    file = open("access_token.txt","r") 
    access_token = file.read() 
    file.close() 

    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    data = '{"context_uri":"spotify:album:5uiLjgmdPV4dgamvmC64Oq","offset":{"position":5},"position_ms":0}'
    url_params = {"device_id":"98bb0735e28656bac098d927d410c3138a4b5bca"}
    response = requests.put('https://api.spotify.com/v1/me/player/play', headers=headers, data=data, params=url_params)
    
    return "BABY PLEASE DON'T GO" + response.text  

@app.route("/radioplay")
def radioplay():
    run("omxplayer", RADIO_STREAM_URL)
    return "LUZ"


@app.route('/cronsave', methods = ['POST'])
def cronsave():
    command = "curl 0.0.0.0:5000/spotiauth && curl 0.0.0.0:5000/spotiplay"
    minutes = request.json['minutes']
    hours = request.json['hours']
    cron_raspi = CronTab(user=SYSTEM_USER)
    cron_raspi.remove_all(comment=ALARM_ADNOTATION_TAG)
    job = cron_raspi.new(command=command, comment=ALARM_ADNOTATION_TAG)
    job.minute.on(minutes)
    job.hour.on(hours)
    cron_raspi.write()
    return "OK"

@app.route('/cronclean', methods = ['GET'])
def cronclean():
    cron_raspi = CronTab(user=SYSTEM_USER)
    cron_raspi.remove_all(comment=ALARM_ADNOTATION_TAG) 
    cron_raspi.write()
    return "CLEANED"


if __name__ == '__main__':
    app.run(debug=True, port=3141, host='0.0.0.0')
