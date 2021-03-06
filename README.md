# spotify-alarm-clock
Takes a time via an http request, saves it to crontab, uses the Spotify API to start playing music at the given (saved) time.

Warning: WIP: the README is lacking and the setup is not smooth

## Installation

```bash
# Get non-python dependencies
sudo apt install curl virtualenv espeak mpc
# Install Raspotify
curl -sL https://dtcooper.github.io/raspotify/install.sh | sh
# Install the Python dependencies in a virtualenv
make dependencies
# Install the systemd service
make install
```

## Systemd service

The server is managed via a systemd service. Here's a quick cheatsheet:

- `systemctl --user status spotify-alarm-clock` - Get general information about the service (like whether it is running and some latest logs).
- `systemctl --user start spotify-alarm-clock` - Start the service manually.
- `systemctl --user stop spotify-alarm-clock` - Stop the service manually.

## Development

- `./virtualenv/bin/python server.py`

