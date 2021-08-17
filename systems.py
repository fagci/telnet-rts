
from queue import Queue
from components import EnergySink, EnergySource, Position, Style
from esper import Processor

class EnergySystem(Processor):
    def process(self):
        for e, (src,) in self.world.get_components(EnergySource):
            for e1, (sink,) in self.world.get_components(EnergySink):
                if sink.src == e:
                    src.capacity -= sink.consumption

class RenderSystem(Processor):
    def __init__(self, q_in:Queue, q_out:Queue):
        self.q_in, self.q_out = q_in, q_out
        
    def process(self):
        self.q_out.put('\u001b[2J')
        for e, (pos, s) in self.world.get_components(Position, Style):
            # self.q_out.put('\033[6n')
            self.q_out.put(f'\033[{pos.x};{pos.y}H{s.icon}')
