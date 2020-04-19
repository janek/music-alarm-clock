import config_reader as cfg

def test_all_config_getters():
	# XXX: can this be done in a loop, so the test doesn't have to be updated for new getters?
	cfg.get_spotify_client_id()
	cfg.get_spotify_client_secret()
	cfg.get_spotify_playable_uri()
	cfg.get_spotify_device_id()
	cfg.get_spotify_refresh_token()