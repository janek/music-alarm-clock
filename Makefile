all:
	@echo Usage: make install 

install:
	# Install the systemd service...
	# Create systemd directories
	mkdir -p ~/.config/systemd/user
	# Copy the service file to systemd directories
	cp spoti.service ~/.config/systemd/user
	# Reload the systemd daemon: https://askubuntu.com/a/1143989/413683
	systemctl --user daemon-reload
	# Enable the service to start system boot (I hope)
	systemctl --user enable spoti
