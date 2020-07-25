from pynput.keyboard import Key, KeyCode, Listener
import requests
from playlists import playlists
from server import play, pause, playpause, set_volume, spotify_request


numlock_modifier_on = False


def on_press(key):
	global numlock_modifier_on
	# 0-9 and /*.-+ are a `KeyCode` with `char` equal to the character on the key and some `vk`
	# enter and numlock are a `KeyCode` with `char` empty but `vk` equal to 76 and 71
	# backspace is a `Key` with enum value Key.backspace
	
	#  __________
	# | N / * - |
	# | 7 8 9 + |
	# | 4 5 6 B |
	# | 1 2 3 E |
	# | 0 0 D E |
	#  __________
	
	# PAGE 2 (numlock off):
	# Key.home, .up, .page_up
	# .left, 65437, .right
	# .end, .down, page_down
	# .insert, .delete, (enter)
	
	try:
		#TODO: how can this form be made clearer? a dictionary with code and action? remember vk vs char
		print(key.vk, key.char)
		if key.vk == 76:
			print("got enter")
			playpause()
		elif key.vk == 71:
			numlock_modifier_on = True
			print("numlock on")
		elif key.char == "-":	
			print("volup")
		elif key.char == "+":
			print("voldown")
		elif key.char == "0":
			print("0 caught")
		elif key.char in [".", ","]:
			playpause()
		elif key.char in ['1','2','3','4','5','6','7','8','9']:
			if numlock_modifier_on:
				set_volume(int(key.char))
				print('set volume to ' + key.char)
				numlock_modifier_on = False
			else:
				print("play num " + key.char)
				play(spotify_uri=playlists[key.char])
		
	except AttributeError:
		print(key)

with Listener(on_press=on_press) as listener:
	listener.join()