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
        from socket import socket, gethostname
        self.so = socket()
        self.so.setblocking(False)
        self.so.bind((gethostname(), 5023))
        self.connections = []
        self.so.listen()

    def render(self, pos, s):
        try:
            connection, address = self.so.accept()
            connection.setblocking(False)
            self.connections.append(connection)
            print('conn:', connection, address)
        except BlockingIOError:
            pass

        for connection in self.connections:
            try:
                message = connection.recv(4096)
            except BlockingIOError:
                continue

            for connection in self.connections:
                connection.send('123')

    def process(self):
        for e, (pos, s) in self.world.get_components(Position, Style):
            self.render(pos, s)
