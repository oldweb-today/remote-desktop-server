FROM oldwebtoday/base-root

# base packages
RUN DEBIAN_FRONTEND=noninteractive apt-get -y update && \
    DEBIAN_FRONTEND=noninteractive apt-get -qqy --no-install-recommends install \
    build-essential \
    python3 \
    python3-pip \
    python3-dev \
    libgstreamer1.0-0 \
    gstreamer-1.0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-alsa \
    gstreamer1.0-pulseaudio \
    gstreamer1.0-tools \
    dbus-x11

# fonts
RUN apt-get -qqy --no-install-recommends install \
    fonts-ipafont-gothic \
    xfonts-100dpi \
    xfonts-75dpi \
    xfonts-cyrillic \
    xfonts-scalable \
    xfonts-base \
    fonts-liberation \
    fonts-arphic-bkai00mp fonts-arphic-bsmi00lp fonts-arphic-gbsn00lp fonts-arphic-gkai00mp fonts-arphic-ukai fonts-farsiweb fonts-nafees fonts-sil-abyssinica fonts-sil-ezra fonts-sil-padauk fonts-unfonts-extra fonts-unfonts-core fonts-indic fonts-thai-tlwg fonts-lklug-sinhala \
  && rm -rf /var/lib/apt/lists/*

# configure pulseaudio
RUN echo "load-module module-native-protocol-tcp auth-ip-acl=0.0.0.0/0 auth-anonymous=1" >> /etc/pulse/default.pa
RUN sed -i '/load-module module-console-kit/s/^/#/' /etc/pulse/default.pa

# env vars
ENV DISPLAY :99

ENV SCREEN_WIDTH 1360
ENV SCREEN_HEIGHT 1020
ENV SCREEN_DEPTH 16

