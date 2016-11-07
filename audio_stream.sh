#!/bin/bash

if [[ "$AUDIO_TYPE" == "opus" ]]; then
    echo "Starting OPUS WS Audio"

    # start ffmpeg
    run_browser /app/ffmpeg -re -f pulse -i default -ac 1 -c:a libopus -ab 64k -frame_duration 2.5 -application lowdelay -listen 1 -f webm tcp://0.0.0.0:4720 > /tmp/ffmpeg.log 2>&1 &

    # start audio proxy
    uwsgi --http-socket :6082 --gevent 4 --wsgi-file /app/audio_proxy.py &

elif [[ "$AUDIO_TYPE" == "raw" ]]; then
    echo "Starting PCM WS Audio"

    run_browser /app/ffmpeg -re -f pulse -i default -ac 1 -ab 64k -ar 44100 -listen 1 -f u8 tcp://0.0.0.0:4720 > /tmp/ffmpeg.log 2>&1 &

    uwsgi --http-socket :6082 --gevent 4 --wsgi-file /app/audio_proxy.py &
fi

