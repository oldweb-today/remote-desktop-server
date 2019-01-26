#!/bin/bash
export GEOMETRY="$SCREEN_WIDTH""x""$SCREEN_HEIGHT""x""$SCREEN_DEPTH"

Xvfb $DISPLAY -listen tcp -screen 0 $GEOMETRY -ac +extension RANDR &

/app/audio_stream.sh &

mkdir -p ~/.vnc 
x11vnc -storepasswd ${VNC_PASS:-secret} ~/.vnc/passwd

# start vnc
x11vnc -forever -ncache_cr -xdamage -usepw -shared -rfbport 5900 -display $DISPLAY > /dev/null 2>&1 &


TIMEOUT_PARAM=""
# add idle-timeout if var set
if [[ -n "$IDLE_TIMEOUT" ]]; then
    TIMEOUT_PARAM="--idle-timeout $IDLE_TIMEOUT"
fi



# run websockify
websockify $TIMEOUT_PARAM 6080 localhost:5900 > /dev/null 2>&1



