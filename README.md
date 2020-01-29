# Remote Desktop Server Contains for Webrecorder/oldweb.today

This repository represents the remote desktop system used by Webrecorder and new oldweb.today
to stream the display and audio from remote browsers.

In Webrecorder/OWT, the system is used to stream contents of web browsers but can apply to any Linux desktop application.

## Desktop Streaming Options

The system provides several connection options for streaming a Linux desktop and audio using VNC and WebRTC.

The options are:

- Full WebRTC: Streaming desktop via WebRTC connection (H264 or VP8) and audio (Opus).

- VNC Video + WebRTC Audio: Streaming desktop via VNC and audio using WebRTC (Opus).

- Vnc Video + WS Audio: Streaming desktop via VNC and audio stream over a WebSocket connection (either MP3 or OPUS)


The `oldwebtoday/remote-desktop-server` supports options for all three and the method can be determined at runtime via the client.

The system is designed to work with an in-browser client, which can determine which connection method to use.
See [oldweb-today/shepherd-client](https://github.com/oldweb-today/shepherd-client) for more info.



## Architecture

The system is comprised of two Docker containers:

- `oldwebtoday/base-displayaudio`: This container sets up the base infrastructure, installing GStreamer, x11vnc, Python, etc.. necessary for streaming

- `oldwebtoday/remote-desktop-server`: This container sets up a Python based media controller, which receives messages via WebSocket. The controller acts
as a signalling server to set up the WebRTC connection. When using streaming audio, it transmits audio packets directly over the WebSocket.
When using VNC, the x11vnc server is used with websockify to transmit VNC data over a separate websocket.

