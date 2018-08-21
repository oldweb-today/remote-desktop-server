#!/bin/bash

if [[ "$AUDIO_TYPE" == "opus" ]]; then
    echo "Starting OPUS WS Audio"

    # opt 1
    uwsgi --http-socket :6082 --gevent 4 --wsgi-file /app/audio_proxy.py &

    # opt 2
    #gst-launch-1.0 -v alsasrc ! audio/x-raw, channels=2, rate=24000 ! opusenc complexity=0 frame-size=2.5 ! webmmux streamable=true ! tcpserversink port=4720 &

    #sleep 2

    #websockify 6082 localhost:4720 &

    # opt 3
    #websockify 6082 -- gst-launch-1.0 -v alsasrc ! audio/x-raw, channels=2, rate=24000 ! opusenc complexity=0 frame-size=2.5 ! webmmux streamable=true ! tcpserversink port=6082 &


elif [[ "$AUDIO_TYPE" == "mp3" ]]; then
    echo "Starting MP3 WS Audio"

    websockify 6082 -- gst-launch-1.0 -v alsasrc ! audio/x-raw, channels=2, rate=24000 ! lamemp3enc target=bitrate cbr=true bitrate=192 ! tcpserversink port=6082 &

fi

