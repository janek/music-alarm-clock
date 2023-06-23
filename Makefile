all:
	@echo Usage:
	@echo make dependencies
	@echo make install
	@echo make restart
	@echo make keyboard-dev

install-audio-receiver:
	wget -q https://github.com/nicokaiser/rpi-audio-receiver/archive/main.zip
	unzip main.zip
	rm main.zip
	sudo ./rpi-audio-receiver-main/install.sh

dependencies: install-audio-receiver
	sudo apt install curl virtualenv espeak mpc mpd
	virtualenv -p /usr/bin/python3 virtualenv
	./virtualenv/bin/pip install --upgrade -r requirements.txt

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
	echo "Reboot is recommended now"

restart:
	systemctl --user restart spotify-alarm-clock

keyboard-dev:
	sudo -E ./virtualenv/bin/python keyboard_control.py

test:
	./virtualenv/bin/pytest
