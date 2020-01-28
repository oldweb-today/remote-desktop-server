#!/bin/bash

echo "### Start Xvfb"
export GEOMETRY="$SCREEN_WIDTH""x""$SCREEN_HEIGHT""x""$SCREEN_DEPTH"

Xvfb $DISPLAY -listen tcp -screen 0 $GEOMETRY -ac +extension RANDR &


echo "### Start x11vnc"
mkdir -p ~/.vnc 
x11vnc -storepasswd ${VNC_PASS:-secret} ~/.vnc/passwd


echo "### Start PulseAudio"
pulseaudio -D


echo "### Start Websockify"
TIMEOUT_PARAM=""
# add idle-timeout if var set
if [[ -n "$IDLE_TIMEOUT" ]]; then
    TIMEOUT_PARAM="--idle-timeout $IDLE_TIMEOUT"
fi

# run websockify
websockify $TIMEOUT_PARAM 6080 localhost:5900 > /dev/null 2>&1 &


echo "### Start Media Controller"
function run_forever() {
    while 'true'
    do
      echo "Execute '$@'"
      "$@"
      sleep 1
    done
}

run_forever python3 -u /app/mediacontroller.py --port 6082




