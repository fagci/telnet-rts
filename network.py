from queue import Queue
from random import randrange
from select import select
from socket import socket, SOL_SOCKET, SO_REUSEADDR
from threading import Lock, Thread

from esper import World

from components import Player, Style, Position

class NetworkThread(Thread):
    world: World
    q_in: Queue
    q_out: Queue
    server: socket
    def __init__(self, world, q_in, q_out, addr='127.0.0.1', port=5023):
        super().__init__()
        self.world = world
        self.addr, self.port = addr, port
        self.q_in, self.q_out = q_in, q_out

        self.server = socket()
        self.server.setblocking(False)
        self.server.bind((addr, port))
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server.listen(5)

        self.connections = {self.server: (None, None)}
        self.c_lock = Lock()
    
    def get_entity(self, s):
        pass

    def run(self):
        while True:
            r,w,e = select(self.connections.keys(), self.connections.keys(), [])
            s:socket

            for s in r:
                if s is self.server:
                    s_fd, addr = self.server.accept()
                    s_fd.setblocking(False)
                    player = self.world.create_entity(
                        Player(),
                        Style(icon='⚉'),
                        Position(randrange(20), randrange(20))
                    )
                    self.connections[s_fd] = (addr, player)
                    print('[+]', addr)
                else:
                    try:
                        data = s.recv(1024)
                        if data:
                            print(f'data:{addr[0]}', data)
                            self.q_in.put(data.decode(errors='ignore'))
                        else:
                            raise ConnectionAbortedError('Client disconnected')
                    except Exception as ex:
                        print(ex)
                        addr, player = self.connections[s]
                        self.world.delete_entity(player)
                        print('[-]', addr)
                        del self.connections[s]
                        s.close()

            while not self.q_out.empty():
                q_data = self.q_out.get()
                for s in w:
                    if s is not self.server:
                        s.send(q_data.encode())


