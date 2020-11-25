import os
from configparser import ConfigParser
from pathlib import Path


# TODO: improve tests, then re-architectre this to not re-instantiate ConfigParser 
# and abstract out saving from set_refresh_tokej
def read_config_file():
    path_of_this_dir, _ = os.path.split(os.path.realpath(__file__))
    config_file_name = "config.ini"
    config_file_path = os.path.join(path_of_this_dir, config_file_name)
    config_parser = ConfigParser()
    num_read_files = config_parser.read(config_file_path)
    assert len(num_read_files) > 0, f'could not read {config_file_path}'
    return config_parser

CONFIG = read_config_file()


def get_spotify_client_id():
    client_id = CONFIG["SPOTIFY"]["CLIENT_ID"]
    validate_id_or_secret(client_id)
    return client_id

def get_spotify_client_secret():
    client_secret = CONFIG["SPOTIFY"]["CLIENT_SECRET"]
    validate_id_or_secret(client_secret)
    return client_secret

def get_spotify_playable_uri():
    spotify_uri = CONFIG["SPOTIFY"]["PLAYABLE_URI"]
    return spotify_uri

def get_spotify_device_id():
    device_id = CONFIG["SPOTIFY"]["DEVICE_ID"]
    return device_id

def get_spotify_refresh_token():
    token = CONFIG["SPOTIFY"]["REFRESH_TOKEN"]
    
    # assert len(token) > 60
    return token
    
def set_spotify_refresh_token(token):
    path_of_this_dir, _ = os.path.split(os.path.realpath(__file__))
    config_file_name = "config.ini"
    config_file_path = os.path.join(path_of_this_dir, config_file_name)
    
    config_parser = ConfigParser()
    config_parser.read(config_file_name)
    config_parser["SPOTIFY"]["REFRESH_TOKEN"] = token
    
    with open(config_file_name, 'w') as configfile:
        config_parser.write(configfile)
    
    
def validate_id_or_secret(value):
    assert len(value) == 32
        
