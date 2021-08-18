from socket import socket, SO_REUSEADDR, SOL_SOCKET
from telnetlib import DO, DONT, ECHO, IAC, NAWS, NEW_ENVIRON, SGA, TTYPE, WILL

def client_loop(s):
    def sendCommand(a, b):
        s.send(IAC + a + b)

    sendCommand(WILL, ECHO);
    sendCommand(DONT, ECHO);
    sendCommand(DO, NAWS);
    sendCommand(WILL, SGA);
    sendCommand(DO, SGA);
    sendCommand(DO, TTYPE);
    sendCommand(DO, NEW_ENVIRON);
    while True:
        try:
            data = s.recv(1024)
            if len(data) == 0:
                s.close()
                break
            print(repr(data))

            for b in data:
                print('C:',int(b))
        except BlockingIOError:
            pass

with socket() as server:
    server.setblocking(False)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 5023))
    server.listen()

    while True:
        try:
            s, addr = server.accept()
            s.setblocking(False)
            client_loop(s)
        except BlockingIOError:
            pass
