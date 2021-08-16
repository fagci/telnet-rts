#!/usr/bin/env python3

from socket import socket, gethostname
from queue import Empty, Queue
from threading import Thread
from time import sleep

from esper import World

from components import Position, Style
from systems import EnergySystem, RenderSystem

world = World()

class NetworkThread(Thread):
    q_in: Queue
    q_out: Queue
    def __init__(self, q_in, q_out, addr='127.0.0.1', port=5023):
        super().__init__()
        self.addr, self.port = addr, port
        self.q_in, self.q_out = q_in, q_out

        self.server = socket()
        self.server.setblocking(False)
        self.server.bind((addr, port))
        self.server.listen(5)

        self.connections = []
    

    def run(self):
        while True:
            try:
                connection, address = self.server.accept()
                connection.setblocking(False)
                self.connections.append(connection)
            except BlockingIOError:
                pass

            for connection in self.connections:
                try:
                    message = connection.recv(1024).decode(errors='ignore')
                    print('got msg:', message)
                    self.q_in.put(message)
                except BlockingIOError:
                    continue

                while self.q_out.not_empty:
                    message = self.q_out.get().encode()
                    for connection in self.connections:
                        print('send msg:', message)
                        try:
                            connection.send(message)
                        except:
                            self.connections.remove(connection)
                            print('some user disconnected')

def main():
    net_q_in = Queue()
    net_q_out = Queue()

    world.add_processor(EnergySystem())
    world.add_processor(RenderSystem(net_q_in, net_q_out))

    world.create_entity(Position(), Style())

    network_thread = NetworkThread(net_q_in, net_q_out)
    network_thread.setDaemon(True)
    network_thread.start()
    print('server listening')

    try:
        while True:
            world.process()
            sleep(0.05)
    except KeyboardInterrupt:
        print('exit')
        exit(130)

if __name__ == '__main__':
    main()
