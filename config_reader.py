from configparser import ConfigParser


def read_config_file():
    config_file_path = "config.ini"
    config_parser = ConfigParser()
    successfully_read_files = config_parser.read(config_file_path)
    assert len(successfully_read_files) > 0, f'could not read {config_file_path}'
    return config_parser


CONFIG = read_config_file()


def get_spotify_client_id():
    '''convenience method to get global feature type'''
    return CONFIG["SPOTIFY"]["CLIENT_ID"]


def get_spotify_client_secret():
    return CONFIG["SPOTIFY"]["CLIENT_SECRET"]