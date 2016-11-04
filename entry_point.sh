#!/bin/bash
export GEOMETRY="$SCREEN_WIDTH""x""$SCREEN_HEIGHT""x""$SCREEN_DEPTH"

mkdir -p ~/.vnc 
x11vnc -storepasswd ${VNC_PASS:-secret} ~/.vnc/passwd

# start xvfb
sudo Xvfb $DISPLAY -screen 0 $GEOMETRY -ac +extension RANDR > /dev/null 2>&1 &

# start ffmpeg
run_browser /app/ffmpeg -re -f pulse -i default -ac 1 -c:a libopus -ab 64k -compression_level 5 -frame_duration 2.5 -application lowdelay -listen 1 -f webm tcp://0.0.0.0:4720 > /tmp/ffmpeg.log 2>&1 &

# start audio proxy
uwsgi --http-socket :6082 --gevent 4 --wsgi-file /app/audio_proxy.py &

if [[ -n "$PROXY_HOST" ]]; then
    export http_proxy=http://$PROXY_HOST:$PROXY_PORT
    export https_proxy=http://$PROXY_HOST:$PROXY_PORT
fi

#wget -O /dev/null "http://set.pywb.proxy/setts?ts=$TS"

function shutdown {
  kill -s SIGTERM $NODE_PID
  wait $NODE_PID
}

# disable any terms
sudo chmod a-x /usr/bin/*term
sudo chmod a-x /bin/*term

# Run browser here
eval "$@" &
  
# start controller app
#python /app/browser_app.py &

autocutsel -s PRIMARY -fork

# start vnc
x11vnc -forever -ncache_cr -xdamage -usepw -shared -rfbport 5900 -display $DISPLAY > /dev/null 2>&1 &


TIMEOUT_PARAM=""
# add idle-timeout if var set
if [[ -n "$IDLE_TIMEOUT" ]]; then
    TIMEOUT_PARAM="--idle-timeout $IDLE_TIMEOUT"
fi

# run websockify
websockify $TIMEOUT_PARAM 6080 localhost:5900 > /dev/null 2>&1 &

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

wait $NODE_PID
