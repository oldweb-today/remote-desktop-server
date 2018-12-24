#!/bin/bash

function run_forever() {
    while 'true'
    do
      echo "Execute '$@'"
      "$@"
      sleep 1
    done
}


echo "##### Start Xvfb"
export GEOMETRY="$SCREEN_WIDTH""x""$SCREEN_HEIGHT""x""$SCREEN_DEPTH"
Xvfb $DISPLAY -listen tcp -screen 0 $GEOMETRY -ac +extension RANDR &


echo "##### Start x11vnc"
mkdir -p ~/.vnc 
x11vnc -storepasswd ${VNC_PASS:-secret} ~/.vnc/passwd

echo "##### Start PulseAudio"
pulseaudio -D

echo "###### Start signaling server"
run_forever python3 -u /app/signaling-server.py --port 6082 &

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
run_forever python3 -u /app/webrtc-sendrecv.py --server ws://localhost:6082 --peer-id 1 &


echo "###### Start X11 "
run_forever x11vnc -forever -ncache_cr -xdamage -usepw -shared -rfbport 5900 -display $DISPLAY > /dev/null 2>&1 &


TIMEOUT_PARAM=""
# add idle-timeout if var set
if [[ -n "$IDLE_TIMEOUT" ]]; then
    TIMEOUT_PARAM="--idle-timeout $IDLE_TIMEOUT"
fi

function shutdown {
  kill -s SIGTERM $NODE_PID
  wait $NODE_PID
}

# disable any terms
sudo chmod a-x /usr/bin/*term
sudo chmod a-x /bin/*term



NODE_PID=$!

trap shutdown SIGTERM SIGINT
for i in $(seq 1 10)
do
  xdpyinfo -display $DISPLAY >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    break
  fi
  echo Waiting xvfb...
  sleep 0.5
done

echo "Xvfb is running"

# Xserver is ready,run websockify
run_forever websockify $TIMEOUT_PARAM 6080 localhost:5900 > /dev/null 2>&1 &

wait $NODE_PID
