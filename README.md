# music-alarm-clock

Takes a time via an http request, saves it to crontab, uses the Spotify API or radio with `mpc` to start playing music at the given (saved) time.

Warning: WIP: the README is lacking and the setup is not smooth

## Setting up the Raspberry Pi

- Install the OS in headless mode following [Tom's Hardware Guide](https://www.tomshardware.com/reviews/raspberry-pi-headless-setup-how-to,6028.html)
- Make sure the timezone of the raspberry pi is the same as your timezone. Locale should be set in the SD flashing process, but consider double-checking. Locale can be very annoying, [this article](https://www.howtoraspberry.com/2020/04/fix-locale-problems-on-raspberry-pi/) can help.
- Consider installing [rpi-audio-receiver](https://github.com/nicokaiser/rpi-audio-receiver).
  - This enables the Raspi to work as music receiver over Spotify Connect, AirPlay and Bluetooth. The script will let you choose which.
  - You can use this repository (in internet radio mode) without any of those. If you want to use Spotify as an alarm clock, you'll need Spotify Connect
  - If the installation doesn't work, consider instaling individual modules separately ([Shairport Sync](https://github.com/mikebrady/shairport-sync/), [Raspotify](https://github.com/dtcooper/raspotify) and others - see also `install.sh` in [rpi-audio-receiver](https://github.com/nicokaiser/rpi-audio-receiver)
  - After installation, Spotify and AirPlay should work immediately, bluetooth could need a restart
  - If you're using a Raspi Zero W, use the [https://github.com/Arcadia197/rpi-audio-receiver]() fork instead. You might run into problems with bluetooth anyway; consider also [this guide](https://gist.github.com/actuino/9548329d1bba6663a63886067af5e4cb)
- Install this repo's contents (below)

## Installation

```bash
# At the moment the path is ~/Developer/spotify-alarm-clock is hardcoded in `spotify-alam-clock.service`, so it's easiest to use it until that's improved
mkdir ~/Developer
cd ~/Developer
git clone https://github.com/janek/spotify-alarm-clock/
cd spotify-alarm-clock

# Install apt dependencies and then Python dependencies in a virtualenv
make dependencies

# Install the systemd service
sudo make install

# Add defalt radio stations - you can also add your own with `mpc add <stream link>`
make radio-staions

# copy sample ini file
cp config.sample.ini config.ini
# configure here:
nano config.ini

```

## Debugging and fixing sound

- `aplay /usr/share/sounds/alsa/Front_Center.wav` is a good test to see if sound works
- `aplay -l` to see what sound devices are visible
- `aplay /usr/share/sounds/alsa/Front_Center.wav -D sysdefault:CARD=1` with 1 or 0, to test specific sound outputs
- for `mpc`/`mpd` to work, do `sudo vi /etc/mpd.conf` and uncomment lines get this result:

```
audio_output {
	type		"alsa"
	name		"My ALSA Device"
}
```

### Sound on Raspberry Zero W with USB sound card

1. `aplay /usr/share/sounds/alsa/Front_Center.wav -D sysdefault:CARD=1` (a.k.a `snd1` if aliases are installed) should work out of the box - if it doesn't, debug that first before going to next steps



2. Update configurations:

```
sudo vim /etc/asound.conf -> add these lines
defaults.pcm.card 1
defaults.ctl.card 1
```

```
sudo vim /usr/share/alsa/alsa.conf -> change 0s to 1s to get the same lines as a result
defaults.pcm.card 1
defaults.ctl.card 1
```

3. Restart

## Optional tips and settings

- `ssh-copy-id -i ~/.ssh/id_ed25519.pub pi@zero-one` to copy your ssh public key and remove the need for a password. Replace `ed25519` by whatever you're using (you can see what's in the folder) and `pi@zero-one` with your username and hostname/ip
- `set -o vi` to use vi shortcuts in terminal
- `make aliases` for useful aliases (see `bash_aliases.sh` to see the contents).
  - (warning: some aliases use `vim` to edit files, which won't work by default. You have to install vim/neovim, or change/alias it to `vi` or `nano`)
  - you can type `alias` to see the list of available aliases (after you install them)
- `sudo vi /etc/motd` + [https://patorjk.com/software/taag](https://patorjk.com/software/taag) to make a friendly welcome message (consider checking "test all" on the website)
- `sudo vi /etc/wpa_supplicant/wpa_supplicant.conf` (or `wifi` if you have aliases) to add additional wifi networks

## Local development with Docker

This project won't run on macOS or Windows (I think). You can use Docker to run the code localy. (Tip for macOS in 2023: [OrbStack](https://orbstack.dev/) is the best way to use Docker).

To build and run:

`make docker-build`
`make docker-run`

You can then connect to it using localhost from machine you're working on, or the IP of that machine when connecting from somewhere else. Verify that it's working with:

`http://localhost:3141/` or e.g. `http://192.168.0.38:3141/`

## Spotify authorization

- Create an app on Spotify and input the Spotify client id into your `config.ini`
- Get the hostname of your Raspberry Pi
- Make sure `http://<your_hostname>:3141/authorize_spotify` is included in "Redirect URIs" on your [Spotify dashboard](https://developer.spotify.com/dashboard/)
  - Internal note: for our Spotify app, some hostnames are pre-authorized already, for example `polywaker-music` or `nice-pi`, also with the `.local` postfix
- Go to `http:/<your_hostname>:3141/login`
- You should see a message that says the access token and refresh tokens have been saved
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
