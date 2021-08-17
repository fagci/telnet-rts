from queue import Queue
from random import randrange
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
from socket import socket, SOL_SOCKET, SO_REUSEADDR
from styles import PLAYER
from threading import Thread

from esper import World

from components import NetworkData, Player, Position

class NetworkThread(Thread):
    world: World
    server: socket
    sel: DefaultSelector
    connections: dict = {}

    def __init__(self, world, host='127.0.0.1', port=5023):
        super().__init__()
        self.world = world
        self.addr = (host, port)

        self.sel = DefaultSelector()


    def accept(self, s, mask):
        s_fd, addr = s.accept()
        s_fd.setblocking(False)
        player_id = self.create_player()
        self.connections[s_fd] = (addr, player_id)
        print('[+]', addr)
        self.sel.register(s_fd, EVENT_READ | EVENT_WRITE, self.communicate)

    def communicate(self, s, mask):
        addr, player_id = self.connections[s]

        if mask & EVENT_READ:
            try:
                data = s.recv(1024)
                if data:
                    print(f'data:{addr[0]}', data, flush=True)
                    nd = self.world.component_for_entity(player_id, NetworkData)
                    nd.q_out.put(data.decode(errors='ignore'))
                else:
                    self.world.delete_entity(player_id)
                    print('[-]')
                    del self.connections[s]
                    self.sel.unregister(s)
                    s.close()
            except Exception as ex:
                print(ex)

        if mask & EVENT_WRITE:
            nd = self.world.component_for_entity(player_id, NetworkData)
            while not nd.q_out.empty():
                s.send(nd.q_out.get().encode())
    
    def run(self):
        self.__create_server()
        self.sel.register(self.server, EVENT_READ, self.accept)
        while True:
            for key, mask in self.sel.select():
                key.data(key.fileobj, mask)

    def create_player(self):
        return self.world.create_entity(
            Player(),
            PLAYER,
            Position(randrange(20), randrange(20)),
            NetworkData()
        )

    def __create_server(self):
        self.server = socket()
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server.setblocking(False)
        self.server.bind(self.addr)
        self.server.listen(16)

