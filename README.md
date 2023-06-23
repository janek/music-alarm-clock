# spotify-alarm-clock
Takes a time via an http request, saves it to crontab, uses the Spotify API to start playing music at the given (saved) time.

Warning: WIP: the README is lacking and the setup is not smooth

## Setting up the Raspberry Pi
- Install the OS in headless mode following [Tom's Hardware Guide](https://www.tomshardware.com/reviews/raspberry-pi-headless-setup-how-to,6028.html)
- Install [rpi-audio-receiver](https://github.com/nicokaiser/rpi-audio-receiver) with the USB audio card already plugged in. Spotify and AirPlay should work immediately, bluetooth could need a restart. 
- Install this repo's contents (below)
- See if radio works by doing `mpc add https://stream.radioluz.pl:8443/luz_hifi.mp3` and `mpc play`. If it's not working, you might need to set it up. Links that could help: [1](https://www.rohberg.ch/de/blog/radio-streaming-with-a-raspberry-pi), [2](https://www.lesbonscomptes.com/pages/raspmpd.html). Set repeat to true. 

## Installation

```bash
# At the moment this path is ~/Developer/spotify-alarm-clock is hardcoded somewhere, so it's easiest to use it until that's fixed
mkdir ~/Developer
git clone https://github.com/janek/spotify-alarm-clock/
cd ~/Developer/

# Install apt dependencies and then Python dependencies in a virtualenv
make dependencies
# Install the systemd service
make install
```

## Systemd service

The server is managed via a systemd service. Here's a quick cheatsheet:

- at the moment the service expects the repository to be located at `/home/pi/Developer/spotify-alarm-clock/` and will not work otherwise. You can change the location in `spotify-alarm-clock.service`
- `systemctl --user status spotify-alarm-clock` - Get general information about the service (like whether it is running and some latest logs).
- `systemctl --user start spotify-alarm-clock` - Start the service manually.
- `systemctl --user stop spotify-alarm-clock` - Stop the service manually.
- `journalctl --user spotify-alarm-clock`

## Spotify authorization
- Create an app on Spotify
- Get the local IP of your raspberry pi, for example `192.168.0.38`
- Make sure `http://192.168.0.38:3141/authorize_spotify` is whitelisted on your [Spotify dashboard](https://developer.spotify.com/dashboard/) (substituting 192.168.0.38 for your raspberry pi's IP)
- Go to `http://192.168.0.38:3141/login` (substituting 192.168.0.38 for your raspberry pi's IP)


## Development

- `./virtualenv/bin/python server.py`

