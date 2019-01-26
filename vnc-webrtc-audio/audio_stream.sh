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

#echo "###### Start signaling server"
#run_forever python3 -u /app/signaling-server.py --port 6082 &

echo "##### Start WebRTC Audio pipeline"

WEBRTC_STUN_SERVER="stun:stun.l.google.com:19302"
#WEBRTC_STUN_SERVER="stun:localhost:3478"
OTHER_ARGS=""
if [ -n "${WEBRTC_STUN_SERVER}" ]; then
  OTHER_ARGS="${OTHER_ARGS} --stun-server ${WEBRTC_STUN_SERVER}"
fi
if [ -n "${WEBRTC_TURN_SERVER}" ]; then
  OTHER_ARGS="${OTHER_ARGS} --turn-server ${WEBRTC_TURN_SERVER}"
fi

#run_forever /app/webrtc-send-webrecorder --signaling-server ws://localhost:6082 --peer-id 1 ${OTHER_ARGS} &
run_forever python3 -u /app/webrtc.py --port 6082

