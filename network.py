from random import randrange
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
from socket import SOL_SOCKET, SO_REUSEADDR, socket
from telnetlib import DO, DONT, ECHO, IAC, NAWS, NEW_ENVIRON, SB, SE, SGA, TTYPE, WILL
from threading import Thread

from esper import World

from components import Disconnect, NetworkData
import prefabs

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


    def communicate(self, s:socket, mask):
        addr, player_id = self.connections[s]

        if mask & EVENT_READ:
            try:
                data = s.recv(1024)
                if data:
                    nd = self.world.component_for_entity(player_id, NetworkData)
                    nd.q_in.put(data)
                else:
                    self.__delete_player(player_id, s, addr)
            except BlockingIOError as e:
                print(repr(e))
            except Exception as ex:
                print(ex)

        if mask & EVENT_WRITE:
            nd = self.world.component_for_entity(player_id, NetworkData)
            while not nd.q_out.empty():
                try:
                    s.send(nd.q_out.get().encode())
                except:
                    self.__delete_player(player_id, s, addr)


    def accept(self, s, _):
        connection, addr = s.accept()
        connection.setblocking(False)

        # tell telnet client to send data asap
        connection.send(IAC + WILL + ECHO);
        connection.send(IAC + DONT + ECHO);
        connection.send(IAC + DO + NAWS);
        connection.send(IAC + WILL + SGA);
        connection.send(IAC + DO + SGA);
        connection.send(IAC + DO + TTYPE);
        connection.send(IAC + DO + NEW_ENVIRON);
        
        self.__create_player(connection, addr)
    

    def run(self):
        self.__create_server()
        self.sel.register(self.server, EVENT_READ, self.accept)
        while True:
            for key, mask in self.sel.select():
                key.data(key.fileobj, mask)

    def __create_player(self, connection, addr):
        player_id = self.world.create_entity(*prefabs.player(1+randrange(19), 1+randrange(19)))
        self.connections[connection] = (addr, player_id)
        self.sel.register(connection, EVENT_READ | EVENT_WRITE, self.communicate)
        print('[+]', player_id, addr)
        return player_id

    def __delete_player(self, player_id, s, addr):
        if self.connections.get(s) is None: # already deleted
            return
        self.world.add_component(player_id, Disconnect())
        del self.connections[s]
        self.sel.unregister(s)
        s.close()
        print('[-]', player_id, addr)

    def __create_server(self):
        self.server = socket()
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server.setblocking(False)
        self.server.bind(self.addr)
        self.server.listen()

