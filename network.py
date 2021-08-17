from random import randrange
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
from socket import SOL_SOCKET, SO_REUSEADDR, socket
from threading import Thread

from esper import World

from components import NetworkData, Player, Position
from styles import PLAYER

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


    def accept(self, s, _):
        s_fd, addr = s.accept()
        s_fd.setblocking(False)
        self.__create_player(s_fd, addr)


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
                    self.__delete_player(player_id, s, addr)
            except Exception as ex:
                print(ex)

        if mask & EVENT_WRITE:
            nd = self.world.component_for_entity(player_id, NetworkData)
            while not nd.q_out.empty():
                try:
                    s.send(nd.q_out.get().encode())
                except:
                    self.__delete_player(player_id, s, addr)
    
    def run(self):
        self.__create_server()
        self.sel.register(self.server, EVENT_READ, self.accept)
        while True:
            for key, mask in self.sel.select():
                key.data(key.fileobj, mask)

    def __create_player(self, s, addr):
        player_id = self.world.create_entity(
            Player(),
            PLAYER,
            Position(randrange(20), randrange(20)),
            NetworkData()
        )
        self.connections[s] = (addr, player_id)
        self.sel.register(s, EVENT_READ | EVENT_WRITE, self.communicate)
        print('[+]', player_id, addr)
        return player_id

    def __delete_player(self, player_id, s, addr):
        self.world.delete_entity(player_id)
        del self.connections[s]
        self.sel.unregister(s)
        s.close()
        print('[-]', player_id, addr)

    def __create_server(self):
        self.server = socket()
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server.setblocking(False)
        self.server.bind(self.addr)
        self.server.listen(16)

