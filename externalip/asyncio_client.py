import asyncio
import sys


@asyncio.coroutine
def run_listener():
    yield asyncio.start_server()


class Listener(object):
    def __init__(self, loop, **kwargs):
        self._loop = loop
        self.kwargs = kwargs
        self.listening_port = asyncio.Future()
        self.received_ip = asyncio.Future()

    @asyncio.coroutine
    def run(self):
        self.server = yield from asyncio.start_server(self.handle_client, port=0,
            **self.kwargs)

        if len(self.server.sockets) != 1:
            raise RuntimeError('More than 1 listening socket?')
        port = self.server.sockets[0].getsockname()[1]
        self.listening_port.set_result(port)


    @asyncio.coroutine
    def handle_client(self, reader, writer):
        data = yield from reader.readline()
        self.received_ip.set_result(data.strip().decode('ascii'))
        self.server.close()


@asyncio.coroutine
def get_external_ip(loop, server=('46.101.132.244', 10050), timeout=5):
    """Connect to the remote server, wait for it to respond with our IP

    Nb. this is a coroutine.

    Args:
        loop : asyncio event loop
        server (tuple): the server address of (host, port)
        timeout (float): seconds to wait before giving up

    Returns:
        str: our external ip in dotted format, or None
    """
    host, port = server

    reader, writer = yield from asyncio.open_connection(host, port)
    writing_socket = writer.get_extra_info('socket')
    socket_family = writing_socket.family

    listener = Listener(loop, family=socket_family)
    loop.create_task(listener.run())

    listening_port = yield from listener.listening_port
    writer.write(u'{}\n'.format(listening_port).encode('ascii'))

    canceller = loop.call_later(timeout, listener.received_ip.cancel)
    try:
        ip = yield from listener.received_ip
    except asyncio.CancelledError:
        ip = None
    else:
        canceller.cancel()
    return ip


if __name__ == '__main__':
    server = ('46.101.132.244', 10050)
    loop = asyncio.get_event_loop()
    ip = loop.run_until_complete(get_external_ip(loop, server))
    loop.close()
    print(ip)
