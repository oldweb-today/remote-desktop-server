#
#   Step 1 build the pipeline
#
FROM ubuntu:18.04 as pipeline_builder
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt-get  -qqy --no-install-recommends install \
    build-essential \
    pulseaudio \
    libopus-dev \
    gstreamer-1.0 \
    gstreamer1.0-tools \
    gstreamer1.0-alsa \
    gstreamer1.0-nice \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-good1.0-dev \
    libgstreamer-plugins-bad1.0-dev \
    libjson-glib-dev \
    libsoup2.4-dev

COPY audio_pipeline /audio_pipeline
RUN cd /audio_pipeline && make

#
# Step 2 The final base image + the builded pipeline
#

FROM oldwebtoday/base-displayaudio
COPY rebind.so /usr/local/lib/rebind.so

RUN DEBIAN_FRONTEND=noninteractive apt-get -y update && \
    DEBIAN_FRONTEND=noninteractive apt-get -qqy --no-install-recommends install \
    x11vnc \
    xvfb \
    sudo \
    pulseaudio \
    alsa-utils \
    gstreamer-1.0 \
    gstreamer1.0-tools \
    gstreamer1.0-alsa \
    gstreamer1.0-nice \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    libjson-glib-dev \
    libsoup2.4-dev \
    socat


WORKDIR /app/

COPY app /app/

COPY --from=pipeline_builder /audio_pipeline/webrtc-send-webrecorder /app

RUN pip3 install -U setuptools pip
RUN pip3 install -U -r /app/requirements.txt

CMD /app/run.sh
