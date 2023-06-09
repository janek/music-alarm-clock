import requests
import json
import schedule
import time
from datetime import datetime
import pytz


def check_device():
    url = "http://192.168.0.38:3141/devices"
    response = requests.get(url, verify=False)
    data = json.loads(response.text)
    devices = data.get("devices", [])
    device_present = "NO"
    for device in devices:
        if device["name"] == "pat-pi":
            device_present = "YES"
            break

    berlin_time = datetime.now(pytz.timezone("Europe/Berlin")).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open("log.txt", "a") as file:
        file.write(f"{berlin_time} - pat-pi present: {device_present}\n")


schedule.every(5).minutes.do(check_device)

while True:
    schedule.run_pending()
    time.sleep(1)
