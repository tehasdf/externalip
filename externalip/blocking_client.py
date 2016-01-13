from contextlib import closing
from datetime import timedelta, datetime
import socket
import select


def parse_server(server):
    if isinstance(server, basestring):
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

    received_buffer = ''

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
                    received_buffer += data
                else:
                    sock.close()
                    to_read.remove(sock)
                    return received_buffer.strip()

        for sock in writing:
            sock.send('%s\n' % (port, ))
            sock.close()
            to_write.remove(sock)


def get_external_ip(server):
    server = parse_server(server)

    with closing(makeServerSocket()) as listeningSocket,\
            closing(socket.create_connection(server)) as connectingSocket:

        return do_loop(listeningSocket, connectingSocket)


if __name__ == '__main__':
    print get_external_ip(('127.0.0.1', 10050))