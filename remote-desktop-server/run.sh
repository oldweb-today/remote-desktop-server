#!/bin/bash

echo "### Start Xvfb"
export GEOMETRY="$SCREEN_WIDTH""x""$SCREEN_HEIGHT""x""$SCREEN_DEPTH"

Xvfb $DISPLAY -listen tcp -screen 0 $GEOMETRY -ac +extension RANDR &


echo "### Init X11 Password"
mkdir -p ~/.vnc 
x11vnc -storepasswd ${VNC_PASS:-secret} ~/.vnc/passwd


echo "### Start PulseAudio"
pulseaudio -D


echo "### Start Media Controller"
function run_forever() {
    while 'true'
    do
      echo "Execute '$@'"
      "$@"
      if [ $? -eq 0 ]; then
        if [[ -n "$IDLE_TIMEOUT" ]]; then
            echo "Waiting for $IDLE_TIMEOUT before exiting..."
            sleep $IDLE_TIMEOUT
        fi
        echo "Done"
        exit 0
      fi

      sleep 1
    done
}

run_forever python3 -u /app/mediacontroller.py --port 6082

