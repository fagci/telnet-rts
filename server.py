#!/usr/bin/env python3

from socket import socket
from select import select
from queue import Queue
from random import randrange
from threading import Lock, Thread
from time import sleep

from esper import World

from components import Player, Position, Style
from systems import EnergySystem, RenderSystem

world = World()

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
                    self.connections[s_fd] = addr
                    self.world.create_entity(
                        Player(),
                        Style(icon='⚉'),
                        Position(randrange(20), randrange(20))
                    )
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
                        print('[-]', self.connections[s])
                        del self.connections[s]
                        s.close()

            while not self.q_out.empty():
                q_data = self.q_out.get()
                for s in w:
                    if s is not self.server:
                        s.send(q_data.encode())


def main():
    net_q_in = Queue()
    net_q_out = Queue()

    world.add_processor(EnergySystem())
    world.add_processor(RenderSystem(net_q_in, net_q_out))

    world.create_entity(Position(), Style())

    network_thread = NetworkThread(world, net_q_in, net_q_out)
    network_thread.setDaemon(True)
    network_thread.start()
    print('server listening')

    try:
        while True:
            world.process()
            sleep(1)
            print('.')
    except KeyboardInterrupt:
        print('exit')
        exit(130)

if __name__ == '__main__':
    main()
