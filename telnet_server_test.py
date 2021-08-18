from socket import socket
import telnetlib

def client_loop(s):
    s.send(telnetlib.IAC + telnetlib.WONT + telnetlib.ECHO)
    s.send(telnetlib.IAC + telnetlib.WONT + telnetlib.NAWS)
    s.send(telnetlib.IAC + telnetlib.DONT + telnetlib.ECHO)
    s.send(telnetlib.IAC + telnetlib.DONT + telnetlib.SGA)
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
    server.bind(('127.0.0.1', 5023))
    server.listen()

    while True:
        try:
            s, addr = server.accept()
            s.setblocking(False)
            client_loop(s)
        except BlockingIOError:
            pass
