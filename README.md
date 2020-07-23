# spoti-alarm-server
Takes a time via an http request, saves it to crontab, uses the Spotify API to start playing music at the given (saved) time.

Warning: WIP: the README is lacking and the setup is not smooth

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

## Usage

- iOS shortcut: https://www.icloud.com/shortcuts/f5d2caf18278496cb99f1f594c5ae398 (change the hardcoded IP to the IP of your server)
