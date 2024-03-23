from server import (
    play,
    pause,
    playpause,
    set_volume,
    radiotoggle,
    radionext,
    increase_volume,
    decrease_volume,
)
from playlists import playlists
import requests
from pynput.keyboard import Key, KeyCode, Listener
import os

print(
    "Starting keyboard listener with $DISPLAY",
    os.environ.get("DISPLAY", "not found in os.environ"),
)

numlock_modifier_on = False


def on_press(key):
    global numlock_modifier_on
    # 0-9 and /*.-+ are a `KeyCode` with `char` equal to the character on the key
    # enter and numlock are a `KeyCode` with `char` empty but `vk` equal to 76 and 71
    # backspace is a `Key` with enum value Key.backspace
    try:
        print(key)
        if key.vk == 76:
            print("got enter")
            playpause()
        elif key.vk == 71:
            numlock_modifier_on = True
            print("numlock on")
        elif key.char == "-":
            print("voldown")
            increase_volume()
        elif key.char == "+":
            print("volup")
            decrease_volume()
        elif key.char == "0":
            playpause()
            print("playpause")
        elif key.char == ".":
            pause()
            print("pause")
        elif key.char in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            if numlock_modifier_on:
                set_volume(int(key.char))
                print("set volume to " + key.char)
                numlock_modifier_on = False
            else:
                print("play num " + key.char)
                play(spotify_uri=playlists[key.char])
    except AttributeError:
        # Happens when key.vk or key.char is empty, i.e. for all `Key`
        # objects
        corresponding_number = get_number_for_numlocked_key(key)
        if corresponding_number:
            vol = corresponding_number / 10
            print("Setting volume to " + str(vol))
            set_volume(vol)
        if key == Key.enter:
            radiotoggle()
            print("Got enter")
        if key == Key.backspace:
            print("Got backspace")
            radionext()


def get_number_for_numlocked_key(key):
    key_map = {
        Key.insert: 0,
        Key.end: 1,
        Key.down: 2,
        Key.page_down: 3,
        Key.left: 4,
        "<65437>": 5,  # This doesn't work at the moment
        Key.right: 6,
        Key.home: 7,
        Key.up: 8,
        Key.page_up: 9,
    }
    return key_map.get(key, None)


with Listener(on_press=on_press) as listener:
    listener.join()
