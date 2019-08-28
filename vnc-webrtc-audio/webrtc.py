import websockets
import asyncio
import os
import sys
import json
import argparse
import logging
import hmac
import base64
import hashlib
import time
from concurrent.futures._base import TimeoutError

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
gi.require_version('GstWebRTC', '1.0')
from gi.repository import GstWebRTC
gi.require_version('GstSdp', '1.0')
from gi.repository import GstSdp


# ============================================================================
AUDIO_PIPELINE = "pulsesrc ! audioconvert ! opusenc ! rtpopuspay ! queue max-size-time=200 min-threshold-time=200000000 max-size-time=220000000  ! capsfilter caps=application/x-rtp,media=audio,encoding-name=OPUS,payload=96"

VP8_PIPELINE = "ximagesrc show-pointer=false ! videoconvert ! queue ! vp8enc deadline=1  buffer-size=100 buffer-initial-size=100 buffer-optimal-size=100 keyframe-max-dist=30 cpu-used=5  ! rtpvp8pay ! queue ! capsfilter caps=application/x-rtp,media=video,encoding-name=VP8,payload=97"
H264_PIPELINE = "ximagesrc show-pointer=false ! videoconvert ! queue ! x264enc tune=0x00000004 key-int-max=30 ! video/x-h264,profile=constrained-baseline,packetization-mode=1 ! rtph264pay ! queue max-size-time=50 ! capsfilter caps=application/x-rtp,media=video,encoding-name=H264,payload=97"

PIPELINES = {'VP8': VP8_PIPELINE,
             'H264': H264_PIPELINE
            }


AUDIO_WEBRTC_PIPELINE = '''
 webrtcbin name=sendrecv bundle-policy=max-bundle
 pulsesrc buffer-time=128000 latency-time=32000  ! audioconvert ! queue ! opusenc frame-size=2.5 ! rtpopuspay !
 queue ! application/x-rtp,media=audio,encoding-name=OPUS,payload=97 ! sendrecv.
'''.format()

# ============================================================================
class WebRTCHandler:
    def __init__(self, ws, keepalive_timeout=30):
        self.ws = ws
        self.pipe = None
        self.webrtc = None
        self.keepalive_timeout = keepalive_timeout

    def send_sdp_offer(self, offer):
        text = offer.sdp.as_text()
        print('Sending offer:\n%s' % text)
        msg = json.dumps({'sdp': {'type': 'offer', 'sdp': text}})

        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.ws.send(msg))

    def on_offer_created(self, promise, _, __):
        promise.wait()
        reply = promise.get_reply()
        offer = reply.get_value('offer')

        promise = Gst.Promise.new()
        self.webrtc.emit('set-local-description', offer, promise)
        promise.interrupt()
        self.send_sdp_offer(offer)

    def on_negotiation_needed(self, element):
        promise = Gst.Promise.new_with_change_func(self.on_offer_created, element, None)
        element.emit('create-offer', None, promise)

    def send_ice_candidate_message(self, _, mlineindex, candidate):

        icemsg = json.dumps({'ice': {'candidate': candidate, 'sdpMLineIndex': mlineindex}})

        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.ws.send(icemsg))

    def generate_rest_api_credentials(self, username, secret):
        # Coturn REST API
        # usercombo -> "timestamp.username",
        # turn user -> usercombo,
        # turn password -> base64(hmac(input_buffer = usercombo, key = shared-secret)).
        time_limit = int(os.environ.get("WEBRTC_TURN_TIME_LIMIT", '3600'))
        separator = os.environ.get("WEBRTC_TURN_REST_API_SEPARATOR", '.').encode()
        turn_username = username.encode()
        turn_secret = secret.encode()
        now = "{}".format(int(time.time() + time_limit)).encode()

        username = separator.join([now, turn_username])
        password = base64.b64encode(hmac.new(turn_secret, username, digestmod=hashlib.sha1).digest())

        return {"username": username.decode("utf8"), "password": password.decode("utf8")}


    def start_pipeline(self, formats):
        pipeline = None
        if os.environ.get('WEBRTC_VIDEO'):
            for format_type in formats:
                pipeline = PIPELINES.get(format_type)
                if pipeline:
                    print('Video Format: ' + format_type)
                    break

            pipeline = pipeline or VP8_PIPELINE
            video = Gst.parse_bin_from_description(pipeline, True)

            audio = Gst.parse_bin_from_description(AUDIO_PIPELINE, True)

            webrtc = Gst.ElementFactory.make("webrtcbin", "sendonly")
            webrtc.set_property('bundle-policy', 'max-bundle')

            pipe = Gst.Pipeline.new('main')

            pipe.add(video)
            pipe.add(audio)
            pipe.add(webrtc)

            video.link(webrtc)
            audio.link(webrtc)

            self.pipe = pipe
        else:
            self.pipe = Gst.parse_launch(AUDIO_WEBRTC_PIPELINE)

        self.webrtc = self.pipe.get_by_name('sendonly')

        self.webrtc.connect('on-negotiation-needed', self.on_negotiation_needed)
        self.webrtc.connect('on-ice-candidate', self.send_ice_candidate_message)
        #self.webrtc.connect('notify::ice-connection-state', self.on_conn_changed)
        self.pipe.set_state(Gst.State.PLAYING)

    async def handle_sdp(self, message):
        assert (self.webrtc)
        msg = json.loads(message)
        if 'sdp' in msg:
            sdp = msg['sdp']
            assert(sdp['type'] == 'answer')
            sdp = sdp['sdp']
            print('Received answer:\n%s' % sdp)
            res, sdpmsg = GstSdp.SDPMessage.new()
            GstSdp.sdp_message_parse_buffer(bytes(sdp.encode()), sdpmsg)
            answer = GstWebRTC.WebRTCSessionDescription.new(GstWebRTC.WebRTCSDPType.ANSWER, sdpmsg)
            promise = Gst.Promise.new()
            self.webrtc.emit('set-remote-description', answer, promise)
            promise.interrupt()
        elif 'ice' in msg:
            ice = msg['ice']
            candidate = ice['candidate']
            sdpmlineindex = ice['sdpMLineIndex']
            self.webrtc.emit('add-ice-candidate', sdpmlineindex, candidate)

    async def loop(self):
        assert self.ws
        while True:
            message = await self.recv_msg_ping()
            iceServers = []
            iceTransportPolicy = 'all'
            if message.startswith('HELLO'):
                formats = json.loads(message[len('HELLO '):])
                if os.environ.get("WEBRTC_STUN_SERVER") is not None:
                    iceServers.append({"urls": os.environ.get("WEBRTC_STUN_SERVER")})
                if os.environ.get("WEBRTC_TURN_REALM") is not None:
                    turn_realm = os.environ.get('WEBRTC_TURN_REALM')
                    turn_server = 'turn:' + turn_realm + '?transport=tcp'

                    username = os.environ.get("REQ_ID") + 'client'
                    secret = os.environ.get('WEBRTC_TURN_REST_AUTH_SECRET')
                    credentials = self.generate_rest_api_credentials(username, secret)
                    iceServers.append({"urls": [turn_server] , "credential": credentials['password'], "username": credentials['username']});
                    iceTransportPolicy = 'relay'

                self.start_pipeline(formats.get('formats', []))

                await self.ws.send('HELLO')
                await self.ws.send(json.dumps({'iceServers':iceServers, 'iceTransportPolicy':iceTransportPolicy}))

            elif message.startswith('ERROR'):
                print(message)
                return 1
            else:
                await self.handle_sdp(message)

        return 0

    async def recv_msg_ping(self):
        '''
        Wait for a message forever, and send a regular ping to prevent bad routers
        from closing the connection.
        '''
        msg = None
        while msg is None:
            try:
                msg = await asyncio.wait_for(self.ws.recv(), self.keepalive_timeout)
                #msg = await self.ws.recv()
            except TimeoutError:
                print('Signaling: Send Keep-Alive Ping')
                await self.ws.ping()

        return msg

    def disconnect(self):
        if self.ws and self.ws.open:
            # Don't care about errors
            asyncio.ensure_future(self.ws.close(reason='hangup'))

        if self.pipe:
            self.pipe.set_state(Gst.State.NULL)


# ============================================================================
class WebRTCServer():
    def __init__(self):
        self.curr = None
        self.keepalive_timeout = 30

    async def handler_loop(self, ws, path=None):
        '''
        All incoming messages are handled here. @path is unused.
        '''
        if self.curr:
            print('Pipeline Already Running?')

        handler = WebRTCHandler(ws, self.keepalive_timeout)
        self.curr = handler

        try:
            await handler.loop()
        except websockets.ConnectionClosed:
            print('Client Disconnected')

        finally:
            print('Closing Connection')
            handler.disconnect()

        print('Exiting')
        sys.exit(0)

    def run_server(self, server_addr, keepalive_timeout):
        print("Signaling: Listening on https://{}:{}".format(*server_addr))

        self.keepalive_timeout = keepalive_timeout

        logger = logging.getLogger('websockets.server')

        logger.setLevel(logging.ERROR)
        logger.addHandler(logging.StreamHandler())

        wsd = websockets.serve(self.handler_loop, *server_addr, max_queue=4)

        asyncio.get_event_loop().run_until_complete(wsd)
        asyncio.get_event_loop().run_forever()

    def check_plugins(self):
        needed = ["opus", "vpx", "nice", "webrtc", "dtls",
                  "srtp", "rtp", "rtpmanager"]

        missing = list(filter(lambda p: Gst.Registry.get().find_plugin(p) is None, needed))
        if len(missing):
            print('Missing gstreamer plugins:', missing)
            return False
        return True


    def init_cli(self):
        Gst.init(None)
        if not self.check_plugins():
            sys.exit(1)

        parser = argparse.ArgumentParser()
        parser.add_argument('--addr', default='0.0.0.0', help='Address to listen on')
        parser.add_argument('--port', default=80, type=int, help='Port to listen on')
        parser.add_argument('--keepalive-timeout', dest='keepalive_timeout', default=30, type=int, help='Timeout for keepalive (in seconds)')

        args = parser.parse_args()

        self.run_server((args.addr, args.port), args.keepalive_timeout)

if __name__=='__main__':
    WebRTCServer().init_cli()


