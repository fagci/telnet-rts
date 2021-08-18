from esper import Processor

from components import EnergySink, EnergySource, NetworkData, Position, Style

class EnergySystem(Processor):
    def process(self):
        for e, (src,) in self.world.get_components(EnergySource):
            for e1, (sink,) in self.world.get_components(EnergySink):
                if sink.src == e:
                    src.capacity -= sink.consumption

class RenderSystem(Processor):
    def process(self):
        for ed, (nd,) in self.world.get_components(NetworkData):
            nd.q_out.put('\033[2J')
            for x in range(21):
                for y in range(21):
                    if x == 0 or x == 20 or y == 0 or y == 20:
                        nd.q_out.put(f'\033[{y+1};{x+1}H█')
                    elif y > 0 and x > 0 and y < 20 and x < 20:
                        nd.q_out.put(f'\033[{y+1};{x+1}H∙')
            for es, (pos, s) in self.world.get_components(Position, Style):
                # nd.q_out.put('\033[6n')
                nd.q_out.put(f'\033[{pos.y+1};{pos.x+1}H{s.icon}')
