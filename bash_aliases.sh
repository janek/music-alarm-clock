alias grep='grep --color=auto'
alias ls='ls --color=auto'

alias cdd='cd ~/Developer/spotify-alarm-clock'
alias rr='sudo shutdown -r now'

alias cfg='vim ~/.bashrc'
alias als='vim ~/.bash_aliases'
alias alsget='curl https://gist.githubusercontent.com/janek/1fdf2824eb80c2325a3abd514d524967/raw > ~/.bash_aliases; source ~/.bashrc'
alias src='source ~/.bashrc'

alias gst='git status'

alias setdisp='echo "export DISPLAY=:0.0" >> ~/.bash_profile; export DISPLAY=:0.0" >> ~/.bashrc'
alias xorg='ps aux | grep Xorg'

alias status='systemctl status raspotify | awk '\''FNR <= 3'\'' && systemctl --user status spotify-alarm-clock | awk '\''FNR <= 3'\'' && systemctl status shairport-sync | awk '\''FNR <= 3'\'' && systemctl --user status spotify-keyboard-controls | awk '\''FNR <= 3'\'''
alias slog='systemctl --user status spotify-alarm-clock -n50'
alias jrn='journalctl -f'

alias snd='aplay /usr/share/sounds/alsa/Front_Center.wav'
alias snd0='aplay /usr/share/sounds/alsa/Front_Center.wav -D sysdefault:CARD=0'
alias snd1='aplay /usr/share/sounds/alsa/Front_Center.wav -D sysdefault:CARD=1'
alias alsaconf='sudo vim /usr/share/alsa/alsa.conf'

alias rur='curl localhost:3141/areyourunning; echo  '
alias splay='curl localhost:3141/spotiplay'
alias sdvs='curl localhost:3141/devices'
alias sauth='curl localhost:3141/request_spotify_authorization; echo  '

alias sres='systemctl --user restart spotify-alarm-clock'
alias sstart='systemctl --user start spotify-alarm-clock'
alias sstop='systemctl --user stop spotify-alarm-clock'

alias kres='systemctl --user restart spotify-keyboard-controls'
alias kstart='systemctl --user start spotify-keyboard-controls'
alias kstop='systemctl --user stop spotify-keyboard-controls'

alias spres='sudo systemctl restart raspotify && espeak "restarting spotify"'

alias servtest='/home/pi/Developer/spotify-alarm-clock/virtualenv/bin/python /home/pi/Developer/spotify-alarm-clock/server.py'
alias vpip='./virtualenv/bin/pip'
alias vpy='./virtualenv/bin/python'

alias gcrec='git clone https://github.com/nicokaiser/rpi-audio-receiver'
alias gcalm='git clone https://github.com/janek/spotify-alarm-clock'