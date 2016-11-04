from gevent import monkey; monkey.patch_all()
import gevent
import gevent.queue

import uwsgi
import socket

q = gevent.queue.Queue()
connected = False


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
            min_packets = 8
            count = 0

            while True:
                buff = sock.recv(16384)
                len_ = len(buff)
                if len_ == last_len and last_len == last_len2 and len_ < min_size:
                    print('Skipping Silence!')
                    continue

                # queue only if connected or first few packets
                if connected or count < min_packets:
                    q.put(buff)

                last_len2 = last_len
                last_len = len_

        except Exception as e:
            print('Stream Error', e)
            gevent.sleep(0.5)


def application(env, start_response):
    # complete the handshake
    uwsgi.websocket_handshake(env['HTTP_SEC_WEBSOCKET_KEY'], env.get('HTTP_ORIGIN', ''))
    global connected
    connected = True
    min_size = 0

    print('WS Connected')

    try:
        buff_tot = ''
        while True:
            buff = q.get()
            buff_tot += buff
            if len(buff_tot) >= min_size:
                uwsgi.websocket_send_binary(buff_tot)
                buff_tot = ''
    except Exception as e:
        print('WS Disconnected', e)
        connected = False

gevent.spawn(load_tcp)
