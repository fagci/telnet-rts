from socket import socket, gethostname
from select import select
from queue import Empty, Queue

from components import EnergySink, EnergySource, Position, Style
from esper import Processor

class EnergySystem(Processor):
    def process(self):
        for e, (src,) in self.world.get_components(EnergySource):
            for e1, (sink,) in self.world.get_components(EnergySink):
                if sink.src == e:
                    src.capacity -= sink.consumption

class RenderSystem(Processor):
    def __init__(self):
        self.so = socket()
        self.so.setblocking(False)
        self.so.bind(('127.0.0.1', 5023))
        self.connections = []
        self.so.listen()
        self.inputs = [self.so]
        self.outputs = []
        self.queue = {}

    def render(self, pos, s):
        readable, writable, exceptional = select(self.inputs, self.outputs, self.inputs)

        for s in readable:
            if s is self.so:
                connection, address = self.so.accept()
                connection.setblocking(False)
                self.inputs.append(connection)
                self.queue[connection] = Queue()
                print('conn:', connection, address)
            else:
                message = s.recv(4096)
                if message:
                    self.queue[s].put(message)
                    if s not in self.outputs:
                        self.outputs.append(s)
                else:
                    if s in self.outputs:
                        self.outputs.remove(s)
                    self.inputs.remove(s)
                    s.close()
                    del self.queue[s]

        for s in writable:
            try:
                next_msg = self.queue[s].get_nowait()
            except Empty:
                self.outputs.remove(s)
            else:
                s.send(next_msg)

        for s in exceptional:
            self.inputs.remove(s)
            if s in self.outputs:
                self.outputs.remove(s)
            s.close()
            del self.queue[s]


    def process(self):
        for e, (pos, s) in self.world.get_components(Position, Style):
            self.render(pos, s)
