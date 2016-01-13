from __future__ import print_function

from externalip.blocking_client import get_external_ip


print(get_external_ip('127.0.0.1:10050'))
