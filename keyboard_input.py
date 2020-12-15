from pynput.keyboard import Key, KeyCode, Listener
import requests
from playlists import playlists
from server import play, pause, playpause, set_volume, previous, next, toggle_shuffle


numpad_keys_without_numlock = [Key.end, Key.down, Key.page_down, 
							Key.left, Key.f1, Key.right, 
							Key.home, Key.up, Key.page_up]
	# Special case: we use f1 as a placeholder for '5',
	# because 5 is not registered in numlock-off layer.
	# (we handle it in the try block with numlock-on keys)

def on_press(key):
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
		# Still unused: /, *, -, 0
		if key.char == '+':
			toggle_shuffle()
		elif key.char in [".", ","]:
			previous()
		elif key.char in ['1','2','3','4','5','6','7','8','9']:
			print("play num " + key.char)
			play(spotify_uri=playlists[key.char])
		elif key.vk == 65437:
			# Special case: this is the "vk" value 
			# of the number 5 when numlock is off.
			# This key is not identifiable otherwise.
			set_volume_step(5)
	except AttributeError:
		# Still unused (.insert)
		if key == Key.enter: 
			playpause()
		elif key == Key.delete:
			next()
		elif key == Key.backspace:
			previous()
		elif key in numpad_keys_without_numlock:
			set_volume_step(numpad_keys_without_numlock.index(key) + 1)
	except Exception:
		print("Exception raised")
		
def set_volume_step(step):
	set_volume(step*10)
	
with Listener(on_press=on_press) as listener:
	listener.join()