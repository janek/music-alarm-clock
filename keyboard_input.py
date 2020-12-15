from pynput.keyboard import Key, KeyCode, Listener
import requests
from server import radiostop, radioplay, radionext


def on_press(key):
    print(key)

with Listener(on_press=on_press) as listener:
    listener.join()
