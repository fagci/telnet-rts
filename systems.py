
from queue import Queue
from components import EnergySink, EnergySource, NetworkData, Position, Style
from esper import Processor

class EnergySystem(Processor):
    def process(self):
        for e, (src,) in self.world.get_components(EnergySource):
            for e1, (sink,) in self.world.get_components(EnergySink):
                if sink.src == e:
                    src.capacity -= sink.consumption

class RenderSystem(Processor):
    def process(self):
        for ed, (nd,) in self.world.get_components(NetworkData):
            nd.q_out.put('\u001b[2J')
            for es, (pos, s) in self.world.get_components(Position, Style):
                # nd.q_out.put('\033[6n')
                nd.q_out.put(f'\033[{pos.x};{pos.y}H{s.icon}')
