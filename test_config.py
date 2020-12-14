import config_reader as cfg


# TODO: in order to test setting token, we need to make a copy of the original config, then change the path config reader is using, then test settting, then remove the copy (or just keep one forever)
mock_refresh_token = "AQDWwdlYhBb4IlgQ5Wo166Q0awes1SXbV66jiWnQERHXN1UHcE9Yq2JoaErOoUgzCJRRETBuOYe1LNyaNngNSqHXnPa_U6h8SM1KFpd_76EurA9BFz6dISBqb4DZig0kQtQ"


def test_all_config_getters():
	# XXX: can this be done in a loop, so the test doesn't have to be updated for new getters?
	cfg.get_spotify_client_id()
	cfg.get_spotify_client_secret()
	cfg.get_spotify_playable_uri()
	cfg.get_spotify_device_id()
	cfg.get_spotify_refresh_token()