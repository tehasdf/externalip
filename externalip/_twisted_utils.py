from twisted.internet.defer import Deferred
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineOnlyReceiver


class ArgumentsFactory(Factory):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def buildProtocol(self, addr):
        proto = self.protocol(*self.args, **self.kwargs)
        proto.factory = self
        return proto


class LineSender(LineOnlyReceiver):
    delimiter = '\n'
    def __init__(self, _line):
        self._line = _line
        self.finished = Deferred()

    def connectionMade(self):
        self.sendLine(self._line)
        self.transport.loseConnection()

    def connectionLost(self, reason):
        self.finished.callback(None)
