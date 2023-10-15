#!/bin/bash

# if this is not run, mpc add does not work properly
mpc update

# Insert track before, use mpc prev, when it finishes and jumps back del the old one
current_track_index=$(mpc -f "%position%" current | tr -d '\n')
random_file=$(ls ~/Developer/voice-messages/ | shuf -n 1)

mpc insert ~/Developer/voice-messages/$random_file

if [ "$current_track_index" -ne "0" ]; then
  mpc move $(($current_track_index + 1)) $current_track_index
fi

mpc prev
sleep 50

# Go back to the initial track and remove the inserted one
mpc del $current_track_index