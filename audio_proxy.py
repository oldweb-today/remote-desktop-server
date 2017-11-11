from gevent import monkey; monkey.patch_all()
import gevent
import gevent.queue

import uwsgi
import socket


# ============================================================================
def application(env, start_response):
    a = AudioProxy()

    if 'HTTP_SEC_WEBSOCKET_KEY' in env:
        a.handle_ws(env)
    else:
        a.handle_http(env, start_response)


# ============================================================================
class AudioProxy(object):
    def __init__(self):
        self.q = gevent.queue.Queue()
        self.connected = True
        self.tcp_source = ('localhost', 4720)
        self.buff_size = 16384*4

    def audio_pull(self):
        while self.connected:
            try:
                sock = socket.socket(socket.AF_INET,
                                     socket.SOCK_STREAM)

                sock.connect(self.tcp_source)

                while self.connected:
                    buff = sock.recv(self.buff_size)
                    self.q.put(buff)

            except Exception as e:
                print('Audio Read Error', e)
                gevent.sleep(0.3)

    def handle_ws(self, env):
        gevent.spawn(self.audio_pull)

        # complete the handshake
        uwsgi.websocket_handshake(env['HTTP_SEC_WEBSOCKET_KEY'],
                                  env.get('HTTP_ORIGIN', ''))
        print('WS Connected')

        try:
            while True:
                buff = self.q.get()
                uwsgi.websocket_send_binary(buff)

        except Exception as e:
            print(e)

        finally:
            self.connected = False
            print('WS Disconnected', e)

    def handle_http(self, env, start_response):
        start_response('200 OK', [('Content-Type', 'webm/audio; codecs="opus"'),
                                  ('Transfer-Encoding', 'chunked')])

        def stream():
            try:
                while True:
                    buff = self.q.get()
                    length = len(buff)
                    if not length:
                        continue

                    yield b'%X\r\n' % length
                    yield buff

            finally:
                self.connected = False

        return stream()


