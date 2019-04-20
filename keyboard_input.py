from pynput.keyboard import Key, KeyCode, Listener
import requests
from playlists import playlists
from server import play

def on_press(key):
	# 0-9 and /*.-+ are a `KeyCode` with `char` equal to the character on the key
	# enter and numlock are a `KeyCode` with `char` empty but `vk` equal to 76 and 71
	# backspace is a `Key` with enum value Key.backspace

	try:
		if key.vk == 76:
			print("got enter")
		elif key.vk == 71:
			print("got numlock")
		elif key.char == "-":

			print("volup")
		elif key.char == "+":

			print("voldown")
		elif key.char == "0":
			print("0 caught")
		elif key.char in ['1','2','3','4','5','6','7','8','9']:
			play(spotify_uri=playlists[key.char])
			print("play num " + key.char)
            

	except AttributeError:
		# Happens when key.vk or key.char is empty, i.e. for all `Key` objects
		if key == Key.backspace:
			print("Got backspace")

with Listener(on_press=on_press) as listener:
	listener.join()