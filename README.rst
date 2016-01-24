external ip
===========

A very simple program to get the external IP of the machine it's run on.

It does it by connecting to a remote server, and having the server try
to connect back to it.
(for now, it uses a public server by default, hosted at 46.101.132.244:10050).

This package contains the server, a twisted client, an asyncio client, and
a blocking client using only py2's stdlib.

Running
-------

To run the tests, cwd to the project directory and do `py.test`.

To run the server, simply do `python -m externalip.server`.

To run the blocking client from the command line, do `python -m externalip`.

To get the IP programatically, use one of the functions:
`externalip.blocking_client.get_external_ip`,
`externalip.asyncio_client.get_external_ip`, or
`externalip.twisted_client.getExternalIP`, depending which flavor of networking
you prefer.


TODO
----
* make the server addr parametrizable from command line...
* add to PyPI?
* tornado-based client
* tests for the blocking client