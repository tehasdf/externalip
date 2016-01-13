from twisted.test.proto_helpers import StringTransport
from externalip._twisted_utils import LineSender


def test_ipsender_sends():
    sender = LineSender('1.2.3.4')
    transport = StringTransport()
    sender.makeConnection(transport)

    assert transport.value() == '1.2.3.4\n'

