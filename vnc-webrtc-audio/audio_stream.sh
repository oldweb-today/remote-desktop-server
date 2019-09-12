#!/bin/bash

function run_forever() {
    while 'true'
    do
      echo "Execute '$@'"
      "$@"
      sleep 1
    done
}

echo "##### Start PulseAudio"
pulseaudio -D

run_forever python3 -u /app/mediacontroller.py --port 6082

