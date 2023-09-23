all:
	@echo Usage:
	@echo make dependencies
	@echo make install
	@echo make restart
	@echo make keyboard-dev

dependencies:
	sudo apt install curl virtualenv espeak mpc mpd
	virtualenv -p /usr/bin/python3 virtualenv
	./virtualenv/bin/pip install --upgrade -r requirements.txt
	echo "Reboot is recommended now"

install:
	# Install the systemd service...
	# Create systemd directories
	mkdir -p ~/.config/systemd/user
	# Copy the service file to systemd directories
	cp spotify-alarm-clock.service ~/.config/systemd/user
	# Reload the systemd daemon: https://askubuntu.com/a/1143989/413683
	systemctl --user daemon-reload
	# Enable the service to start system boot (I hope)
	systemctl --user enable spotify-alarm-clock

aliases:
	cat bash_aliases >> ~/.bash_aliases
	source ~/.bashrc

radio-stations:
	mpc add https://stream-relay-geo.ntslive.net/stream
	mpc add https://stream-relay-geo.ntslive.net/stream2
	mpc add https://streaming.radio.co/s3699c5e49/listen

restart:
	systemctl --user restart spotify-alarm-clock

keyboard-dev:
	sudo -E ./virtualenv/bin/python keyboard_control.py

test:
	./virtualenv/bin/pytest
