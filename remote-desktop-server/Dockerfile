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

COPY rebind.so /usr/local/lib/rebind.so

COPY . /app/

RUN ln -s /usr/lib/python2.7/config-x86_64-linux-gnu/libpython2.7.so /usr/lib/libpython2.7.so

CMD /app/run.sh


