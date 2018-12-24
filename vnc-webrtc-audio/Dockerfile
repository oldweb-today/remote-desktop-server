FROM oldwebtoday/vnc-ws-audio

WORKDIR /app/

COPY app/requirements.txt /app/

RUN pip3 install -U setuptools pip
RUN pip3 install -U -r /app/requirements.txt

COPY app /app/

CMD /app/run.sh
