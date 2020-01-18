# spoti-alarm-server
Raspberry + Spotify alarm clock server

Work in progress, README will be updated when the project is share-ready.

## Systemd service

The server is managed via a systemd service. Here's a quick cheatsheet:

- `systemctl --user status spoti` - Get general information about the service (like whether it is running and some latest logs).
- `systemctl --user start spoti` - Start the service manually.
- `systemctl --user stop spoti` - Stop the service manually.
