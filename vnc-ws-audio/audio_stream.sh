#!/bin/bash

pulseaudio -D

if [[ "$AUDIO_TYPE" == "opus" ]]; then
    echo "Starting OPUS WS Audio"

    websockify 6082 -- gst-launch-1.0 -v pulsesrc buffer-time=128000 latency-time=32000 ! audioconvert ! opusenc frame-size=2.5 ! webmmux ! tcpserversink port=6082 &


elif [[ "$AUDIO_TYPE" == "mp3" ]]; then
    echo "Starting MP3 WS Audio"

    websockify 6082 -- gst-launch-1.0 -v pulsesrc buffer-time=128000 latency-time=32000 ! audioconvert ! lamemp3enc target=bitrate cbr=true bitrate=192 ! tcpserversink port=6082 &
fi

