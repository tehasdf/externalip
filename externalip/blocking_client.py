from __future__ import print_function

from contextlib import closing
from datetime import timedelta, datetime
import socket
import select


def parse_server(server):
    if isinstance(server, str):
        host, _, port = server.partition(':')
        if not port:
            port = 10050
        else:
            port = int(port)
        return (host, port)

    return server


def makeServerSocket():
    listeningSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listeningSocket.bind(('', 0))
    listeningSocket.listen(1)

    return listeningSocket


def accept_connection(listeningSocket):
    connection, addr = listeningSocket.accept()
    connection.setblocking(0)
    return connection


def do_loop(listeningSocket, connectingSocket, timeout=5):
    port = listeningSocket.getsockname()[1]

    to_read = [listeningSocket]
    to_write = [connectingSocket]

    received_buffer = u''

    start_time = datetime.now()
    while True:
        if datetime.now() - start_time > timedelta(seconds=timeout):
            return None

        reading, writing, exc = select.select(to_read, to_write , to_read + to_write, 0.1)
        for sock in reading:
            if sock is listeningSocket:
                connection = accept_connection(listeningSocket)
                to_read.append(connection)
            else:
                data = sock.recv(1024)
                if data:
                    received_buffer += data.decode('ascii')
                else:
                    sock.close()
                    to_read.remove(sock)
                    return received_buffer.strip()

        for sock in writing:
            sock.send(u'{}\n'.format(port).encode('ascii'))
            sock.close()
            to_write.remove(sock)


def get_external_ip(server, timeout):
    """Connect to the remote server, wait for it to respond with our IP

    Args:
        server (tuple): the server address of (host, port)
        timeout (float): seconds to wait before giving up

    Returns:
        str: our external ip in dotted format, or None
    """
    server = parse_server(server)

    with closing(makeServerSocket()) as listeningSocket,\
            closing(socket.create_connection(server)) as connectingSocket:

        return do_loop(listeningSocket, connectingSocket, timeout)


if __name__ == '__main__':
    print(get_external_ip(('46.101.132.244', 10050)))
