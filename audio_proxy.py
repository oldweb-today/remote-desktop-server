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

            while True:
                buff = sock.recv(16384)
                print(len(buff))
                q.put(buff)

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
