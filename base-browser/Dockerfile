FROM ubuntu:bionic

# fonts
RUN DEBIAN_FRONTEND=noninteractive apt-get -y update && \
    DEBIAN_FRONTEND=noninteractive apt-get -qqy --no-install-recommends install \
    fonts-liberation \
    fonts-dejavu \
    fonts-arphic-ukai fonts-arphic-uming fonts-ipafont-mincho fonts-ipafont-gothic fonts-unfonts-core \
    fonts-indic \
    fonts-noto-color-emoji


# basic
RUN DEBIAN_FRONTEND=noninteractive apt-get -y update && \
    DEBIAN_FRONTEND=noninteractive apt-get -qqy --no-install-recommends install \
    jwm \
    wmctrl \
    sudo \
    dnsutils \
    libssl-dev \
    libffi-dev \
    net-tools \
    libnss3-tools \
    curl \
    socat \
    wget \
    pulseaudio \
    dbus-x11 \
    ca-certificates \
    bzip2

## sudo
RUN useradd browser --shell /bin/bash --create-home \
  && usermod -a -G sudo browser \
  && echo 'ALL ALL = (ALL) NOPASSWD: ALL' >> /etc/sudoers \
  && echo 'browser:secret' | chpasswd



WORKDIR app

COPY jwmrc /home/browser/.jwmrc

ADD run_forever /usr/bin/run_forever

ADD browser_entrypoint.sh /app/browser_entrypoint.sh

USER browser

ENTRYPOINT ["/app/browser_entrypoint.sh"]

