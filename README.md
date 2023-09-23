# spotify-alarm-clock

Takes a time via an http request, saves it to crontab, uses the Spotify API to start playing music at the given (saved) time.

Warning: WIP: the README is lacking and the setup is not smooth

## Setting up the Raspberry Pi

- Install the OS in headless mode following [Tom's Hardware Guide](https://www.tomshardware.com/reviews/raspberry-pi-headless-setup-how-to,6028.html)
- Make sure the timezone of the raspberry pi is the same as your timezone
- Install [rpi-audio-receiver](https://github.com/nicokaiser/rpi-audio-receiver) with the USB audio card already plugged in. Spotify and AirPlay should work immediately, bluetooth could need a restart.
- Install this repo's contents (below)

## Installation

```bash
# At the moment this path is ~/Developer/spotify-alarm-clock is hardcoded somewhere, so it's easiest to use it until that's fixed
mkdir ~/Developer
cd ~/Developer
git clone https://github.com/janek/spotify-alarm-clock/

# Install apt dependencies and then Python dependencies in a virtualenv
make dependencies

# Install the systemd service
make install

# copy sample ini file
cp config.sample.ini config.ini 
# configure here:
nano config.ini

```

## Running

`curl <your_pi_ip_address>:3141/areyourunning` or go to `http://<your_pi_ip_address_or_hostname>:3141/areyourunning` in your browser

## Spotify authorization

- Create an app on Spotify
- Get the local IP of your raspberry pi, for example `192.168.0.38`
- Make sure `http://192.168.0.38:3141/authorize_spotify` is included in "Redirect URIs" on your [Spotify dashboard](https://developer.spotify.com/dashboard/) (substituting 192.168.0.38 for your raspberry pi's IP)
- Go to `http://192.168.0.38:3141/login` (substituting 192.168.0.38 for your raspberry pi's IP)
- Edit `/etc/raspotify/conf` and add the following:
  LIBRESPOT_USERNAME="<your_spotify_username"
  LIBRESPOT_PASSWORD="<your_spotify_password"
  - (without this the device will "disappear" from the /devices/ endpoint of the Spotify API and will not be reachable for the alarm)

## Configuring radio stations

- If you ran `make dependencies`, you should have `mpd` and `mpc` installed. You can run `sudo apt install mpd mpc` to be sure.
- Edit `/etc/mpd.conf` and uncomment or add lines to say the following:
  ```sh
    audio_output {
      type "alsa"
      name "My ALSA Device"
    }
  ```
- Set repeat on to be able to switch back-and-forth between stations: `mpc repeat true`
- Links that could help if you get stuck: [1](https://www.rohberg.ch/de/blog/radio-streaming-with-a-raspberry-pi), [2](https://www.lesbonscomptes.com/pages/raspmpd.html)

## Systemd service

The server is managed via a systemd service. Here's a quick cheatsheet:

- at the moment the service expects the repository to be located at `/home/pi/Developer/spotify-alarm-clock/` and will not work otherwise. You can change the location in `spotify-alarm-clock.service`
- `systemctl --user status spotify-alarm-clock` - Get general information about the service (like whether it is running and some latest logs).
- `systemctl --user start spotify-alarm-clock` - Start the service manually.
- `systemctl --user stop spotify-alarm-clock` - Stop the service manually.
- `journalctl --user spotify-alarm-clock`

## Development

- `./virtualenv/bin/python server.py`
