FROM balenalib/raspberrypi4-64-debian-python:latest

# Set working directory
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
        curl \
        virtualenv \
        espeak \
        mpc \
        mpd

# Create a virtual environment and activate it
RUN virtualenv venv

# If you have a requirements.txt, copy and install using pip within the virtual environment
COPY requirements.txt ./
RUN . venv/bin/activate && pip install --no-cache-dir -r requirements.txt

# Create a non-root user (optional but recommended for security)
RUN useradd -m pi
USER pi

# Copy the rest of your project
COPY . .

# Set the default command for the container using the virtual environment's Python
CMD [ "venv/bin/python", "./server.py" ]
