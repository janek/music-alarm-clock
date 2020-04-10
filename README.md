# spoti-alarm-server
Takes a time via an API, saves a time to crontab, uses the Spotify API to start playing music at the given time.

Work in progress, README will be updated

## Installation

```bash
# Get dependencies: cURL for Raspotify and virtualenv for the project
sudo apt install curl virtualenv
# Install Raspotify
curl -sL https://dtcooper.github.io/raspotify/install.sh | sh
# Install the Python dependencies in a virtualenv
make dependencies
# Install the systemd service
make install
```

## Systemd service

The server is managed via a systemd service. Here's a quick cheatsheet:

- `systemctl --user status spoti` - Get general information about the service (like whether it is running and some latest logs).
- `systemctl --user start spoti` - Start the service manually.
- `systemctl --user stop spoti` - Stop the service manually.
