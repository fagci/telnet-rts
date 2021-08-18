from esper import Processor, World

from components import Connect, Dirty, Disconnect, EnergySink, EnergySource, NetworkData, Position, Room, Style

class EnergySystem(Processor):
    def process(self):
        for e, (src,) in self.world.get_components(EnergySource):
            for e1, (sink,) in self.world.get_components(EnergySink):
                if sink.src == e:
                    src.capacity -= sink.consumption

class PlayerConnectionSystem(Processor):
    def process(self):
        for e, (src,) in self.world.get_components(Disconnect):
            self.world.remove_component(e, Disconnect)
            self.world.delete_entity(e)
            for r, (room,) in self.world.get_components(Room):
                self.world.add_component(r, Dirty())
        for e, (src,) in self.world.get_components(Connect):
            self.world.remove_component(e, Connect)
            self.world.add_component(e, Dirty())

class RenderSystem(Processor):
    world: World
    def process(self):
        for _, (dirty,) in self.world.get_components(Dirty):
            for r, (room,) in self.world.get_components(Room):
                self.world.add_component(r, Dirty())
            for r, (position,) in self.world.get_components(Position):
                self.world.add_component(r, Dirty())

        for ed, (nd,) in self.world.get_components(NetworkData):
            for r, (room, dirty) in self.world.get_components(Room, Dirty):
                nd.q_out.put('\033[2J')

                x1, x2 = room.x, room.x + room.w
                y1, y2 = room.y, room.y + room.h

                for x in range(x1, x2+1):
                    for y in range(y1, y2+1):
                        if x == x1 or x == x2 or y == y1 or y == y2:
                            nd.q_out.put(f'\033[{y+1};{x+1}H█')
                        elif y > y1 and x > x1 and y < y2 and x < x2:
                            nd.q_out.put(f'\033[{y+1};{x+1}H∙')

            for es, (pos, s, dirty) in self.world.get_components(Position, Style, Dirty):
                # nd.q_out.put('\033[6n')
                nd.q_out.put(f'\033[{pos.y+1};{pos.x+1}H{s.icon}')
        for r, (dirty,) in self.world.get_components(Dirty):
            self.world.remove_component(r, Dirty)
