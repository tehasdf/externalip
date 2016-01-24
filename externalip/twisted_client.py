
import sys

from twisted.internet import reactor
from twisted.internet.endpoints import clientFromString, TCP4ClientEndpoint, TCP4ServerEndpoint, connectProtocol
from twisted.internet.defer import inlineCallbacks, Deferred, returnValue, CancelledError
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineOnlyReceiver
from twisted.python import log

from externalip._twisted_utils import ArgumentsFactory, LineSender


def _getClientEndpoint(reactor, server):
    if isinstance(server, str):
        return clientFromString(reactor, server)
    else:
        host, port = server
        return TCP4ClientEndpoint(reactor, host, port)


class IPReceiver(LineOnlyReceiver):
    delimiter = b'\n'
    def __init__(self, finished):
        self.finished = finished

    def lineReceived(self, line):
        addr = line.strip()
        self.finished.callback(addr)
        self.transport.loseConnection()


class _ReceiverFactory(Factory):
    def __init__(self, finished):
        self._finished = finished

    def buildProtocol(self, addr):
        proto = IPReceiver(self._finished)
        proto.factory = self
        return proto


def makeServer(reactor):
    endpoint = TCP4ServerEndpoint(reactor, 0)
    finished = Deferred()
    return (endpoint.listen(ArgumentsFactory.forProtocol(IPReceiver, finished))
        .addCallback(lambda listeningPort: (finished, listeningPort.getHost().port))
    )


def sendQuery(server, port):
    proto = LineSender(str(port).encode('ascii'))
    return connectProtocol(server, proto).addCallback(lambda proto: proto.finished)


@inlineCallbacks
def getExternalIP(reactor=reactor, server='tcp:46.101.132.244:10050', timeout=5):
    """Connect to the remote server, wait for it to respond with our IP

    Nb. this is a coroutine.

    Args:
        reactor : a twisted reactor
        server (str): strports description of the server, eg. "tcp:1.2.3.4:8080"
                      OR a tuple: the server address of (host, port)
        timeout (float): seconds to wait before giving up

    Returns:
        Deferred(str): our external ip in dotted format, or None
    """
    endpoint = _getClientEndpoint(reactor, server)

    response, port = yield makeServer(reactor)
    reactor.callLater(timeout, response.cancel)
    yield sendQuery(endpoint, port)

    try:
        addr = yield response
    except CancelledError:
        returnValue(None)

    returnValue(addr.decode('ascii'))
