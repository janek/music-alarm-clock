import json
from flask import Flask, request, redirect, g, render_template
import requests
from urllib.parse import quote
import base64

# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response.


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
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080

REF_TOKEN = "AQD3owby0pWQOqv1G2WIXGrDiV-EQ5doMPdes5YllKJ9Pu0QO2_EojrjfY4EOVPEN9YAH7Ln82_8bGj9gy8xDapcCRNy5U7qlNmzFwsU3wNdps69HF-VgPOre5EBdaSxBCOzWA"


@app.route("/spotiauth")
def spotiauth():
    global access_token
    # Ask for a new authorization token, using the refresh token, CLIENT_ID and CLIENT_SECRET 
    code_payload = {
        "grant_type": "refresh_token",
        "refresh_token": REF_TOKEN
    }

    auth_str = '{}:{}'.format(CLIENT_ID,CLIENT_SECRET)
    b64_auth_str = base64.urlsafe_b64encode(auth_str.encode()).decode()

    authorization_header = {"Authorization": "Basic {}".format(b64_auth_str)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=authorization_header)

    response_data = json.loads(post_request.text)
    new_access_token = response_data["access_token"]
    access_token = new_access_token 

    file = open("access_token.txt","w") 
    file.write(access_token) 
    file.close() 

    return access_token

@app.route("/spotiplay")
def spotiplay():
    file = open("access_token.txt","r") 
    access_token = file.read() 
    file.close() 

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(access_token)
    }

    data = '{"context_uri":"spotify:album:5uiLjgmdPV4dgamvmC64Oq","offset":{"position":5},"position_ms":0}'

    response = requests.put('https://api.spotify.com/v1/me/player/play', headers=headers, data=data)
    # response = requests.put(SPOTIFY_PLAY_URL, headers=headers, data=data)
    return "BABY PLEASE DON'T GO"  




app.run(debug=True, port=PORT)