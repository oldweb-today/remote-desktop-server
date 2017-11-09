from gevent import monkey; monkey.patch_all()
import gevent
import gevent.queue

import uwsgi
import socket


# ============================================================================
q = None
connected = False


# ============================================================================
def load_tcp():
    global connected
    global q

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', 4720))

            last_len = -1
            last_len2 = -1
            min_size = 4000
            min_first_packets = 2
            first_buff = ''
            count = 0
            q = gevent.queue.Queue()

            while True:
                buff = sock.recv(16384)
                count += 1

                # queue only if connected or first few packets
                if count < min_first_packets:
                    first_buff += buff
                elif count == min_first_packets:
                    first_buff += buff
                    q.put(first_buff)
                    first_buff = None
                elif connected:
                    len_ = len(buff)
                    if (min_size > 0 and len_ < min_size and
                        len_ == last_len and last_len == last_len2):
                        continue

                    q.put(buff)

                    last_len2 = last_len
                    last_len = len_
                else:
                    last_len = last_len2 = 0

        except Exception as e:
            print('Stream Error', e)
            gevent.sleep(0.5)


# ============================================================================
def application(env, start_response):
    if 'HTTP_SEC_WEBSOCKET_KEY' in env:
        handle_ws(env)
    else:
        handle_http(env, start_response)


# ============================================================================
def handle_ws(env):
    global q
    global connected
    connected = True

    # complete the handshake
    uwsgi.websocket_handshake(env['HTTP_SEC_WEBSOCKET_KEY'],
                              env.get('HTTP_ORIGIN', ''))
    print('WS Connected')

    try:
        while True:
            try:
                buff = q.get()
                uwsgi.websocket_send_binary(buff)
            except AttributeError:
                gevent.sleep(0.5)
                print('Q Init Wait')

    except Exception as e:
        print(e)

    finally:
        print('WS Disconnected', e)
        connected = False


# ============================================================================
def handle_http(env, start_response):
    start_response('200 OK', [('Content-Type', 'webm/audio; codecs="opus"'),
                              ('Transfer-Encoding', 'chunked')])

    global connected
    connected = True

    def stream():
        while True:
            buff = q.get()
            length = len(buff)
            if not length:
                continue

            yield b'%X\r\n' % length
            yield buff

    return stream()



gevent.spawn(load_tcp)
