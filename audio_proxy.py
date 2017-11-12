from gevent import monkey; monkey.patch_all()
import gevent
import gevent.queue

import uwsgi
import socket
import subprocess

curr_conn = None


# ============================================================================
def application(env, start_response):
    global curr_conn
    if curr_conn:
        curr_conn.close()

    curr_conn = AudioProxy()

    if 'HTTP_SEC_WEBSOCKET_KEY' in env:
        curr_conn.handle_ws(env)
    else:
        curr_conn.handle_http(env, start_response)


# ============================================================================
class AudioProxy(object):
    PORT = 4720
    AUDIO_CMD = 'gst-launch-1.0 -v alsasrc ! cutter threshold=0.002 ! audioconvert ! audioresample ! opusenc frame-size=2.5 ! webmmux ! tcpserversink port={0}'

    def __init__(self):
        self.connected = True
        self.buff_size = 16384*4
        self.start_proc()

    def start_proc(self):
        self.port = AudioProxy.PORT
        print('Starting Audio Server on Port {0}'.format(self.port))
        self.tcp_source = ('localhost', self.port)

        args = self.AUDIO_CMD.format(self.port).split(' ')
        self.proc = subprocess.Popen(args)

        AudioProxy.PORT += 1

    def get_audio_buff(self):
        while self.connected:
            try:
                sock = socket.socket(socket.AF_INET,
                                     socket.SOCK_STREAM)

                sock.connect(self.tcp_source)

                while self.connected:
                    buff = sock.recv(self.buff_size)
                    yield buff

            except Exception as e:
                print('Audio Read Error', e)
                if self.proc.poll() is not None:
                    self.start_proc()

                gevent.sleep(0.3)

        yield None

    def handle_ws(self, env):
        # complete the handshake
        uwsgi.websocket_handshake(env['HTTP_SEC_WEBSOCKET_KEY'],
                                  env.get('HTTP_ORIGIN', ''))
        print('WS Connected')

        try:
            for buff in self.get_audio_buff():
                if not buff:
                    break

                uwsgi.websocket_send_binary(buff)

        except Exception as e:
            import traceback
            traceback.print_exc()

        finally:
            self.close()
            print('WS Disconnected')

    def handle_http(self, env, start_response):
        start_response('200 OK', [('Content-Type', 'webm/audio; codecs="opus"'),
                                  ('Transfer-Encoding', 'chunked')])

        print('HTTP Conn')

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
                self.close()

        return stream()

    def close(self):
        self.connected = False
        self.proc.kill()

