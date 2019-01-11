FROM ubuntu:bionic

# Adapted from https://github.com/radiokit/docker-gstreamer/blob/master/Dockerfile
RUN apt-get -y update

# Install compiler etc.
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
  autoconf \
  automake \
  autopoint \
  bison \
  flex \
  libtool \
  yasm \
  nasm \
  git-core \
  build-essential \
  gettext \
  pulseaudio \
  gtk-doc-tools

# Install dependencies necessary to build our custom GStreamer build
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
  libglib2.0-dev \
  libpthread-stubs0-dev \
  libssl-dev \
  liborc-dev \
  libmpg123-dev \
  libmp3lame-dev \
  libsoup2.4-dev \
  libshout3-dev \
  libpulse-dev \
  libopus-dev \
  libgirepository1.0-dev \
  libsrtp2-dev \
  libvpx-dev \
  libx11-dev \
  libxv-dev \
  libxt-dev \
  #libx264-dev \
  libgnutls28-dev \
  python-gi-dev \
  python-dev


ARG GIT_BRANCH=master

# Fetch and build GStreamer
RUN git clone -b $GIT_BRANCH --depth 1 git://anongit.freedesktop.org/git/gstreamer/gstreamer && \
cd gstreamer && \
git checkout $GIT_BRANCH && \
./autogen.sh --prefix=/usr --disable-gtk-doc && \
make -j`nproc` && \
make install && \
cd .. && \
rm -rvf /gstreamer

# Fetch and build gst-plugins-base
RUN git clone -b $GIT_BRANCH --depth 1 git://anongit.freedesktop.org/git/gstreamer/gst-plugins-base && \
cd gst-plugins-base && \
git checkout $GIT_BRANCH && \
./autogen.sh --prefix=/usr \
--disable-gtk-doc \
--disable-adder \
--disable-app \
#--disable-videoconvert \
--disable-gio \
--disable-subparse \
#--disable-tcp \
#--disable-videotestsrc \
--disable-videorate \
--disable-videoscale \
#--disable-x \
--disable-xvideo \
--disable-xshm \
--disable-alsa \
--disable-cdparanoia \
--disable-ivorbis \
--disable-libvisual \
--disable-pango \
--disable-theora && \
make -j`nproc` && \
make install && \
cd .. && \
rm -rvf /gst-plugins-base


# libnice
ARG LIB_NICE_VERSION=0.1.15

RUN git clone -b $LIB_NICE_VERSION git://anongit.freedesktop.org/libnice/libnice \
&& cd libnice \
&& git checkout $LIB_NICE_VERSION \
&& ./autogen.sh --prefix=/usr --with-gstreamer --enable-static --enable-static-plugins --enable-shared --without-gstreamer-0.10 --disable-gtk-doc --enable-compile-warnings=no \
&& make install && \
cd .. && \
rm -rvf /libnice


# Fetch and build gst-plugins-good
RUN git clone -b $GIT_BRANCH --depth 1 git://anongit.freedesktop.org/git/gstreamer/gst-plugins-good && \
cd gst-plugins-good && \
git checkout $GIT_BRANCH && \
./autogen.sh --prefix=/usr \
--disable-gtk-doc \
--disable-alpha \
--disable-avi \
--disable-deinterlace \
--disable-dtmf \
--disable-effectv \
--disable-flv \
--disable-flx \
--disable-goom \
--disable-goom2k1 \
--disable-imagefreeze \
--disable-interleave \
--disable-isomp4 \
#--disable-matroska \
--disable-monoscope \
#--disable-rtp \
#--disable-rtpmanager \
--disable-rtsp \
--disable-shapewipe \
--disable-smpte \
--disable-udp \
--disable-videobox \
--disable-videocrop \
--disable-videofilter \
--disable-videomixer \
--disable-y4m \
--disable-directsound \
--disable-waveform \
--disable-oss \
--disable-oss4 \
--disable-sunaudio \
--disable-osx_audio \
--disable-osx_video \
--disable-gst_v4l2 \
#--disable-x \
--disable-aalib \
--disable-aalibtest \
--disable-cairo \
--disable-flac \
--disable-gdk_pixbuf \
--disable-jack \
--disable-jpeg \
--disable-libcaca \
--disable-libdv \
--disable-libpng \
--disable-dv1394 \
#--disable-vpx 
&& \
make -j`nproc` && \
make install && \
cd .. && \
rm -rvf /gst-plugins-good

# Fetch and build gst-plugins-bad
#RUN git clone -b $GIT_BRANCH --depth 1 git://anongit.freedesktop.org/git/gstreamer/gst-plugins-bad && \
#cd gst-plugins-bad && \
#git checkout $GIT_BRANCH && \
RUN git clone -b webrtc-port-range --depth 1 https://gitlab.freedesktop.org/ikreymer/gst-plugins-bad.git && \
cd gst-plugins-bad && \
git checkout webrtc-port-range && \
./autogen.sh --prefix=/usr \
--disable-gtk-doc \
--disable-accurip \
--disable-adpcmdec \
--disable-adpcmenc \
--disable-aiff \
--disable-videoframe_audiolevel \
--disable-asfmux \
--disable-compositor \
--disable-bayer \
--disable-camerabin2 \
--disable-coloreffects \
--disable-dvbsuboverlay \
--disable-dvdspu \
--disable-faceoverlay \
--disable-festival \
--disable-fieldanalysis \
--disable-freeverb \
--disable-frei0r \
--disable-gaudieffects \
--disable-geometrictransform \
--disable-gdp \
--disable-inter \
--disable-interlace \
--disable-ivfparse \
--disable-ivtc \
--disable-jp2kdecimator \
--disable-jpegformat \
--disable-librfb \
--disable-midi \
--disable-mpegdemux \
--disable-mpegtsdemux \
--disable-mpegtsmux \
--disable-mpegpsmux \
--disable-mxf \
--disable-netsim \
--disable-onvif \
--disable-pcapparse \
--disable-pnm \
--disable-rawparse \
--disable-sdp \
--disable-siren \
--disable-smooth \
--disable-speed \
--disable-subenc \
--disable-timecode \
--disable-videofilters \
--disable-videoparsers \
--disable-videosignal \
--disable-vmnc \
--disable-y4m \
--disable-yadif \
--disable-directsound \
--disable-wasapi \
--disable-direct3d \
--disable-winscreencap \
--disable-winks \
--disable-android_media \
--disable-apple_media \
--disable-bluez \
--disable-avc \
--disable-shm \
--disable-vcd \
--disable-opensles \
--disable-uvch264 \
--disable-nvenc \
--disable-tinyalsa \
--disable-msdk \
--disable-assrender \
--disable-voamrwbenc \
--disable-voaacenc \
--disable-bs2b \
--disable-bz2 \
--disable-chromaprint \
--disable-curl \
--disable-dash \
--disable-dc1394 \
--disable-decklink \
--disable-directfb \
--disable-wayland \
--disable-webp \
--disable-daala \
--disable-dts \
--disable-resindvd \
--disable-faac \
--disable-faad \
--disable-fbdev \
--disable-fdk_aac \
--disable-flite \
--disable-gsm \
--disable-fluidsynth \
--disable-kate \
--disable-kms \
--disable-ladspa \
--disable-lv2 \
--disable-libde265 \
--disable-libmms \
#--disable-srtp \
#--disable-dtls \
--disable-ttml \
--disable-modplug \
--disable-mpeg2enc \
--disable-mplex \
--disable-musepack \
--disable-neon \
--disable-ofa \
--disable-openal \
--disable-opencv \
--disable-openexr \
--disable-openh264 \
--disable-openjpeg \
--disable-openmpt \
--disable-openni2 \
--disable-rsvg \
--disable-gl \
--disable-gtk3 \
--disable-qt \
--disable-vulkan \
--disable-teletextdec \
--disable-wildmidi \
--disable-smoothstreaming \
--disable-sndfile \
--disable-soundtouch \
--disable-spc \
--disable-gme \
--disable-dvb \
--disable-acm \
--disable-vdpau \
--disable-sbc \
--disable-schro \
--disable-zbar \
--disable-rtmp \
--disable-spandsp \
--disable-hls \
--disable-x265 \
--disable-webrtcdsp && \
make -j`nproc` && \
make install && \
cd .. && \
rm -rvf /gst-plugins-bad && echo ""


# Fetch and build gst-plugins-ugly
RUN git clone -b $GIT_BRANCH --depth 1 git://anongit.freedesktop.org/git/gstreamer/gst-plugins-ugly && \
cd gst-plugins-ugly && \
git checkout $GIT_BRANCH && \
./autogen.sh --prefix=/usr \
--disable-gtk-doc \
--disable-asfdemux \
--disable-dvdlpcmdec \
--disable-dvdsub \
--disable-xingmux \
--disable-realmedia \
--disable-a52dec \
--disable-amrnb \
--disable-amrwb \
--disable-cdio \
--disable-dvdread \
--disable-sidplay \
--disable-x264 \
&& \
make -j`nproc` && \
make install && \
cd .. && \
rm -rvf /gst-plugins-ugly


ARG GST_PY_VERSION=1.14

# install gst-python
RUN git clone -b $GST_PY_VERSION --depth 1 git://anongit.freedesktop.org/git/gstreamer/gst-python && \
cd gst-python && \
git checkout $GST_PY_VERSION && \
./autogen.sh --prefix=/usr && \
make -j`nproc` && \
make install && \
cd .. && \
rm -rvf /gst-python

# Do some cleanup
RUN DEBIAN_FRONTEND=noninteractive apt-get clean && \
apt-get autoremove -y

# configure pulseaudio
RUN echo "load-module module-native-protocol-tcp auth-anonymous=1 auth-ip-acl=0.0.0.0/0" >> /etc/pulse/default.pa
RUN echo "load-module module-native-protocol-unix auth-anonymous=1 socket=/tmp/.X11-unix/pulse-socket" >> /etc/pulse/default.pa

RUN sed -i '/load-module module-console-kit/s/^/#/' /etc/pulse/default.pa

# env vars
ENV DISPLAY :99

ENV SCREEN_WIDTH 1360
ENV SCREEN_HEIGHT 1020
ENV SCREEN_DEPTH 16

