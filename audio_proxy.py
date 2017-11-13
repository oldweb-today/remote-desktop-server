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
        print('Close Prev')
        curr_conn.close()

    curr_conn = AudioProxy()

    if 'HTTP_SEC_WEBSOCKET_KEY' in env:
        curr_conn.handle_ws(env)
    else:
        return curr_conn.handle_http(env, start_response)


# ============================================================================
class AudioProxy(object):
    PORT = 4720
    AUDIO_CMD = 'gst-launch-1.0 -v alsasrc ! audio/x-raw, channels=2, rate=24000 ! cutter ! opusenc complexity=0 frame-size=2.5 ! webmmux ! tcpserversink port={0}'

    def __init__(self):
        self.connected = True
        self.buff_size = 16384*4
        self.proc = None

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

    def handle_ws(self, env):
        # complete the handshake
        uwsgi.websocket_handshake(env['HTTP_SEC_WEBSOCKET_KEY'],
                                  env.get('HTTP_ORIGIN', ''))

        print('WS Connected: ' + env.get('QUERY_STRING', ''))

        ready = uwsgi.websocket_recv()

        print('Ready, Starting Audio Stream')

        self.start_proc()
        gevent.sleep(0.3)

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
        content_type = 'audio/webm; codecs="opus"'
        start_response('200 OK', [('Content-Type', content_type),
                                  ('Transfer-Encoding', 'chunked')])

        print('HTTP Connection')

        self.start_proc()
        gevent.sleep(0.3)

        def stream():
            total_buff = b''
            try:
                for buff in self.get_audio_buff():
                    if not buff:
                        break

                    total_buff += buff
                    length = len(total_buff)

                    if length < 1024:
                        continue

                    yield b'%X\r\n' % length
                    yield total_buff
                    yield b'\r\n'
                    total_buff = b''

                yield b'0\r\n\r\n'

            except:
                import traceback
                traceback.print_exc()

            finally:
                self.close()

        return stream()

    def close(self):
        self.connected = False
        if self.proc:
            self.proc.kill()

