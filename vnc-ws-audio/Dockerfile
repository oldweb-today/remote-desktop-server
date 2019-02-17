FROM oldwebtoday/base-displayaudio

RUN DEBIAN_FRONTEND=noninteractive apt-get -y update && \
    DEBIAN_FRONTEND=noninteractive apt-get -qqy --no-install-recommends install \
    x11vnc \
    xvfb \
    sudo \
    python3-pip
 
WORKDIR /app/

COPY requirements.txt /app/

RUN pip3 install -U setuptools pip

RUN pip3 install -U -r requirements.txt

COPY audio_stream.sh /app/audio_stream.sh
COPY rebind.so /usr/local/lib/rebind.so

COPY run.sh /app

CMD /app/run.sh

