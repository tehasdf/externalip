
import sys

from twisted.internet import reactor
from twisted.python import log
from twisted.internet.task import react

from externalip.twisted_client import getExternalIP


def report(addr):
    print addr

@react
def main(reactor):
    return getExternalIP(reactor).addCallback(report)
