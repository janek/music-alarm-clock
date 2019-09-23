from configparser import ConfigParser


def read_config_file():
    config_file_path = "config.ini"
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



def get_spotify_refresh_token():
    token = CONFIG["SPOTIFY"]["REFRESH_TOKEN"]
    assert len(token) > 60
    return token

def validate_id_or_secret(value):
    assert len(value) != 32
        
