from esper import Processor, World

from components import Connect, Dirty, Disconnect, EnergySink, EnergySource, NetworkData, Position, Room, Style

class System(Processor):
    """Fix types, ease access to methods"""
    world: World
    def get_components(self, *args) -> list[tuple[int, tuple]]:
        return self.world.get_components(*args)
    def remove_component(self, e, c):
        return self.world.remove_component(e, c)
    def add_component(self, e, c):
        return self.world.add_component(e, c)
    def delete_entity(self, e):
        return self.world.delete_entity(e)

class EnergySystem(System):
    def process(self):
        for e, (src,) in self.get_components(EnergySource):
            for e1, (sink,) in self.get_components(EnergySink):
                if sink.src == e:
                    src.capacity -= sink.consumption

class PlayerConnectionSystem(System):
    def process(self):
        for e, (src,) in self.get_components(Disconnect):
            self.remove_component(e, Disconnect)
            self.delete_entity(e)
            for r, (room,) in self.get_components(Room):
                self.add_component(r, Dirty())
        for e, (src,) in self.get_components(Connect):
            self.remove_component(e, Connect)
            self.add_component(e, Dirty())

class RenderSystem(System):
    def mv(self, x, y, text=''):
        return f'\033[{y+1};{x+1}H{text}'

    def cls(self):
        return '\033[2J'

    def process(self):
        # TODO: hierarchy update
        for _, (dirty,) in self.get_components(Dirty):
            for r, (room,) in self.get_components(Room):
                self.add_component(r, Dirty())
            for r, (position,) in self.get_components(Position):
                self.add_component(r, Dirty())

        for ed, (nd,) in self.get_components(NetworkData):
            output = []
            for r, (room, dirty) in self.get_components(Room, Dirty):
                output.append(self.cls())

                x1, x2 = room.x, room.x + room.w
                y1, y2 = room.y, room.y + room.h

                for x in range(x1, x2+1):
                    for y in range(y1, y2+1):
                        if x == x1 or x == x2 or y == y1 or y == y2:
                            output.append(self.mv(x,y,'█'))
                        elif y > y1 and x > x1 and y < y2 and x < x2:
                            output.append(self.mv(x,y,'∙'))

            for es, (pos, s, dirty) in self.get_components(Position, Style, Dirty):
                output.append(self.mv(pos.x, pos.y, s.icon))

            nd.q_out.put(''.join(output))

        for r, (dirty,) in self.get_components(Dirty):
            self.remove_component(r, Dirty)
