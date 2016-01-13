
import sys

from twisted.internet import reactor
from twisted.internet.endpoints import clientFromString, TCP4ClientEndpoint, TCP4ServerEndpoint, connectProtocol
from twisted.internet.defer import inlineCallbacks, Deferred, returnValue
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineOnlyReceiver
from twisted.python import log

from externalip._twisted_utils import ArgumentsFactory, LineSender


def _getClientEndpoint(reactor, server):
    if isinstance(server, basestring):
        return clientFromString(reactor, server)
    else:
        host, port = server
        return TCP4ClientEndpoint(reactor, host, port)


class IPReceiver(LineOnlyReceiver):
    delimiter = '\n'
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
    proto = LineSender('%s' % (port, ))
    return connectProtocol(server, proto).addCallback(lambda proto: proto.finished)


@inlineCallbacks
def getExternalIP(reactor=reactor, server='tcp:127.0.0.1:10050'):
    endpoint = _getClientEndpoint(reactor, server)

    response, port = yield makeServer(reactor)
    yield sendQuery(endpoint, port)
    addr = yield response
    returnValue(addr)
