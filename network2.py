from queue import Queue
from random import randrange
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
from socket import socket, SOL_SOCKET, SO_REUSEADDR
from styles import PLAYER
from threading import Thread

from esper import World

from components import Player, Position

class NetworkThread(Thread):
    world: World
    q_in: Queue
    q_out: Queue
    server: socket
    sel: DefaultSelector
    connections: dict = {}

    def __init__(self, world, q_in, q_out, addr='127.0.0.1', port=5023):
        super().__init__()
        self.world = world
        self.q_in, self.q_out = q_in, q_out

        self.sel = DefaultSelector()

        self.__create_server(addr, port)

    def accept(self, s, mask):
        s_fd, addr = s.accept()
        # s_fd.setblocking(False)
        player = self.create_player()
        self.connections[s_fd] = (addr, player)
        print('[+]', addr)
        self.sel.register(s_fd, EVENT_READ | EVENT_WRITE, self.communicate)

    def communicate(self, s, mask):
        addr, player = self.connections[s]

        if mask & EVENT_READ:
            try:
                data = s.recv(1024)
                if data:
                    print(f'data:{addr[0]}', data)
                    self.q_in.put(data.decode(errors='ignore'))
                else:
                    self.world.delete_entity(player)
                    print('[-]')
                    del self.connections[s]
                    s.close()
            except Exception as ex:
                print(ex)

        if mask & EVENT_WRITE:
            while not self.q_out.empty():
                q_data = self.q_out.get()
                if s is not self.server:
                    s.send(q_data.encode())
    
    def run(self):
        self.sel.register(self.server, EVENT_READ, self.accept)
        while True:
            for key, mask in self.sel.select():
                key.data(key.fileobj, mask)

    def create_player(self):
        return  self.world.create_entity(
            Player(),
            PLAYER,
            Position(randrange(20), randrange(20))
        )

    def __create_server(self, addr, port):
        self.server = socket()
        self.server.setblocking(False)
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server.bind((addr, port))
        self.server.listen(5)


