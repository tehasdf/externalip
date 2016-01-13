import sys

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint, connectProtocol
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineOnlyReceiver
from twisted.python import log

from externalip._twisted_utils import ArgumentsFactory, LineSender


class IPSender(object):
    def __init__(self, reactor):
        self._reactor = reactor

    def sendIP(self, host, port):
        endpoint = TCP4ClientEndpoint(self._reactor, host, port)
        senderProto = LineSender(host.encode('ascii'))
        connectProtocol(endpoint, senderProto)


class IPGetter(LineOnlyReceiver):
    delimiter = b'\n'
    def __init__(self, sender):
        self._sender = sender

    def lineReceived(self, line):
        try:
            port = int(line)
        except ValueError:
            self.transport.loseConnection()
            return
        addr = self.transport.getPeer()
        self.sendIP(addr.host, port)

    def sendIP(self, host, port):
        self._sender.sendIP(host, port)
        self.transport.loseConnection()


if __name__ == '__main__':
    sender = IPSender(reactor)
    endpoint = TCP4ServerEndpoint(reactor, 10050)
    endpoint.listen(ArgumentsFactory.forProtocol(IPGetter, sender))
    log.startLogging(sys.stdout)
    reactor.run()
