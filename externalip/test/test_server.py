from pytest import fixture
from twisted.internet.address import IPv4Address
from externalip.server import IPGetter


class _MockIPSender(object):
    """Pass this in instead of a real IPSender, and then examine the ._sendTo
    attribute.
    """
    _sendTo = None
    def sendIP(self, host, port):
        self._sendTo = (host, port)


class _MockTransport(object):
    connectionLost = False

    def __init__(self, addr):
        self._addr = addr

    def getPeer(self):
        return self._addr

    def loseConnection(self):
        self.connectionLost = True


@fixture
def mock_ipsender():
    return _MockIPSender()


def test_ipgetter_receives_port(mock_ipsender):
    mock_transport = _MockTransport(IPv4Address('TCP', '1.2.3.4', 44556))
    getter = IPGetter(mock_ipsender)
    getter.makeConnection(mock_transport)

    getter.lineReceived('443\n')

    assert mock_ipsender._sendTo == ('1.2.3.4', 443)
    assert mock_transport.connectionLost == True


def test_ipgetter_receives_garbage(mock_ipsender):
    mock_transport = _MockTransport(IPv4Address('TCP', '1.2.3.4', 44556))
    getter = IPGetter(mock_ipsender)
    getter.makeConnection(mock_transport)

    getter.lineReceived('asd\n')

    assert mock_ipsender._sendTo is None
    assert mock_transport.connectionLost == True
