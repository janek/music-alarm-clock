all:
	@echo Usage:
	@echo make dependencies
	@echo make install
	@echo make aliases
	@echo make radio-stations
	@echo make restart
	@echo make keyboard-dev
	@echo make test


dependencies:
	sudo apt install curl virtualenv espeak mpc mpd
	virtualenv -p /usr/bin/python3 virtualenv
	./virtualenv/bin/pip install --upgrade -r requirements.txt
	echo "Reboot is recommended now"

install:
	# Install the systemd service
	# For the program to run in the background and start on boot
	sudo cp spotify-alarm-clock.service /etc/systemd/system
	sudo systemctl daemon-reload
	sudo systemctl enable spotify-alarm-clock

aliases:
	cat bash_aliases >> ~/.bash_aliases
	source ~/.bashrc

radio-stations:
	mpc add https://stream-relay-geo.ntslive.net/stream
	mpc add https://stream-relay-geo.ntslive.net/stream2
	mpc repeat on

restart:
	sudo systemctl restart spotify-alarm-clock

keyboard-dev:
	sudo -E ./virtualenv/bin/python keyboard_control.py

test:
	./virtualenv/bin/pytest
