import socket
import select



if __name__ == '__main__':

    listeningSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listeningSocket.bind(('', 0))
    listeningSocket.listen(1)
    port = listeningSocket.getsockname()[1]

    connectingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connectingSocket.connect(('127.0.0.1', 10050))

    to_read = [listeningSocket]
    to_write = [connectingSocket]
    connected = set()
    while True:
        reading, writing, exc = select.select(to_read, to_write , to_read + to_write, 0.1)
        for sock in reading:
            if sock is listeningSocket:
                connection, addr = sock.accept()
                to_read.append(connection)
                connection.setblocking(1)
                connected.add(connection)
            else:
                data = sock.recv(1024)
                if data:
                    print 'recv', data
                else:
                    sock.close()
                    to_read.remove(sock)

        for sock in writing:
            sock.send('%s\n' % (port, ))
            sock.close()
            to_write.remove(sock)
