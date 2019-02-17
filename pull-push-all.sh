#!/bin/bash

action=pull
echo "$1"

if [ ! -z $1 ]; then
  action=$1
fi

docker $action oldwebtoday/base-displayaudio
docker $action oldwebtoday/vnc-ws-audio
docker $action oldwebtoday/vnc-webrtc-audio

