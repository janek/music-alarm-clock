import json
import time
import threading
from flask import Flask, request, redirect, url_for, Response

from subprocess import run
import subprocess
from crontab import CronTab
import os
import logging
import telebot


app = Flask(__name__)
log = logging.getLogger(__name__) # gets the app.logger

from media import app_media
app.register_blueprint(app_media)

from media import *

# App's global constants
SYSTEM_USER = os.environ.get('USER')

ALARM_ANNOTATION_TAG = "SPOTIFY ALARM"  # Identifies our lines in crontab
currently_playing = False
fade_minutes = 1

@app.route("/spotialarm")
def spotialarm():
   log.info('Starting spotify alarm') 
   global fade_minutes
   start_fading_volume_in_thread(goal_volume=70, fade_duration_mins=fade_minutes)
   spotiplay()
   return "Spotify alarm started"

@app.route("/radioalarm")
def radioalarm():
    log.info('Starting radio alarm')
    global fade_minutes
    start_fading_volume_in_thread(goal_volume=70, fade_duration_mins=fade_minutes)
    radioplay()
    return "Radio alarm started"


def start_fading_volume_in_thread(goal_volume=70, fade_duration_mins=1):
    # start fade_volume in a new thread
    fade_thread = threading.Thread(target=fade_volume, args=(goal_volume, fade_duration_mins))
    fade_thread.start()

def fade_volume(goal_volume=70, fade_duration_mins=1):
    global fade_minutes
    print("Fading for " + str(fade_minutes)  + " mins")
    sleep_time = 2
    steps = float(fade_duration_mins * 60) / sleep_time

    for i in range(int(steps)):
        start_time = time.time()
        set_volume(float(i) / float(steps) * goal_volume)
        while ((time.time()-start_time)< sleep_time):
            time.sleep(0.1)
        
    set_volume(goal_volume)

@app.route("/volume")
def volume():
    new_volume = request.args.get('volume')
    set_volume(new_volume)
    return "Volume set to " + str(new_volume) if new_volume is not None else "Volume not set"

def set_volume(new_volume):
    print(new_volume)
    if (new_volume == 0):
        set_volume_master(new_volume)
    elif (new_volume< 5):
        set_volume_master(new_volume*10)
    elif (new_volume< 10):
        set_volume_master(100)

    set_volume_spotify(new_volume)

def set_volume_master(new_volume):
    run(["amixer", "set", "Master", str(new_volume) + "%"])


def say(something):
    run(["espeak", something], stdout=subprocess.DEVNULL)


@app.route('/cronsave', methods=['POST'])
def cronsave():
    global fade_minutes
    minutes = request.json['minutes']
    hours = request.json['hours']
    music_mode = request.json['mode']

    if 'fade_minutes' in request.json:
        fade_minutes = request.json['fade_minutes']

    if music_mode == "luz" or music_mode == "radio":
        command = "curl " + THIS_SERVER_ADDRESS + "/radioalarm"
    else:
        command = "curl " + THIS_SERVER_ADDRESS + "/spotialarm"
    cron_raspi = CronTab(user=SYSTEM_USER)
    cron_raspi.remove_all(comment=ALARM_ANNOTATION_TAG)
    job = cron_raspi.new(command=command, comment=ALARM_ANNOTATION_TAG)
    job.minute.on(minutes)
    job.hour.on(hours)
    cron_raspi.write()
    log.info("Alarm set to " + str(hours) + ":" + str(minutes))
    return "Alarm saved!"

@app.route('/cronclean', methods=['GET'])
def cronclean():
    cron_raspi = CronTab(user=SYSTEM_USER)
    cron_raspi.remove_all(comment=ALARM_ANNOTATION_TAG)
    cron_raspi.write()
    return "All alarms cleared."

@app.route('/areyourunning', methods=['GET'])
def areyourunning():
    message = "Alarm-clock server is running."
    say(message)
    return message

############################################

BOT_TOKEN = '6273214149:AAFvK4UXOGb-Vy0bTjbXq5FWVCowtZuBFRc'
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.repl
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    print(message.text)
    #bot.reply_to(message, message.text)


def start_bot():
    try:
        bot.infinity_polling(interval=1, timeout=1)
    except: 
        pass

if __name__ == '__main__':
    log.setLevel(logging.INFO)

    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()

    # TODO eventually deploy ?!
    app.run(debug=True, port=PORT, host='0.0.0.0')

    bot.stop()
    bot_thread.join()

