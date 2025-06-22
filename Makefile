all:
	@echo Usage:
	@echo make dependencies
	@echo make install
	@echo make aliases
	@echo make radio-stations
	@echo make restart
	@echo make keyboard-dev
	@echo make test
	@echo make docker-build
	@echo make docker-run


dependencies:
	sudo apt install curl virtualenv espeak mpc mpd mpg123 neovim
	virtualenv -p /usr/bin/python3 virtualenv
	./virtualenv/bin/pip install --upgrade -r requirements.txt
	echo "Reboot is recommended now"

install:
	# Install the systemd service
	# For the program to run in the background and start on boot
	sudo cp spotify-alarm-clock.service /etc/systemd/system
	sudo systemctl daemon-reload
	sudo systemctl enable spotify-alarm-clock

install-keyboard:
	sudo cp keyboard-controls.service /etc/systemd/system
	sudo systemctl daemon-reload
	sudo systemctl enable keyboard-controls
  
aliases:
	cat bash_aliases >> ~/.bash_aliases
	source ~/.bashrc

radio-stations:
	mpc add https://stream-relay-geo.ntslive.net/stream # https://nts.live/
	mpc add https://stream-relay-geo.ntslive.net/stream2 # https://nts.live/
	# mpc add https://streaming.radio.co/s3699c5e49/listen # https://refugeworldwide.com/, might have tech issues / not work
	# mpc add https://stream.radiokampus.fm/kampus # https://radiokampus.fm/
	# mpc add https://stream.radioluz.pl:8443/luz_hifi.mp3 # https://radioluz.pl/, might have tech issues
	mpc repeat on

restart:
	sudo systemctl restart spotify-alarm-clock

dev:
	/home/pi/Developer/spotify-alarm-clock/virtualenv/bin/python /home/pi/Developer/spotify-alarm-clock/server.py

numpad: 
	nohup make keyboard-dev > /dev/null 2>&1 &

keyboard-dev:
	sudo -E ./virtualenv/bin/python keyboard_input.py

test:
	./virtualenv/bin/pytest

docker-build:
	docker build -t spotify-alarm-clock:latest .

docker-run:
	docker run -it -p 3141:3141 spotify-alarm-clock:latest

