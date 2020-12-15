from pynput.keyboard import Key, KeyCode, Listener
import requests
from server import say, radiostop, radioplay, radionext

def on_press(key):
    print(key)
    try:
        if key.char == '/':
            radiostop()
            say("Stopping radio")
        if key.char == '*':
            radioplay()
            say("Starting radio")
        if key.char == '-':
            radionext()
            say("Playing next station")
    except Exception:
        print("Hit an exception")

with Listener(on_press=on_press) as listener:
    listener.join()
