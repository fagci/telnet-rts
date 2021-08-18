from esper import Processor, World

from components import Connect, Dirty, Disconnect, EnergySink, EnergySource, NetworkData, Player, Position, Room, Style

from styles import C, BC, SC

class System(Processor):
    """Fix types, ease access to methods"""
    world: World
    def get_components(self, *args) -> list[tuple[int, tuple]]:
        return self.world.get_components(*args)
    def remove_component(self, e, c):
        print('[c-]', e, c)
        return self.world.remove_component(e, c)
    def add_component(self, e, c):
        print('[c+]', e, c)
        return self.world.add_component(e, c)
    def delete_entity(self, e):
        print('[e-]', e)
        return self.world.delete_entity(e)
    def has_component(self, e, c):
        return self.world.has_component(e, c)

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
            if self.has_component(e, Dirty):
                self.delete_entity(e)
            else:
                self.add_component(e, Dirty())
        for e, (src,) in self.get_components(Connect):
            self.remove_component(e, Connect)
            self.add_component(e, Dirty())

class RenderSystem(System):
    def mv(self, x=0, y=0, text=''):
        return f'\033[{y+1};{x+1}H{text}'

    def cls(self):
        return '\033[2J'

    def color_fg(self, c):
        return f'\033[38;5;{c}m'

    def color_bg(self, c):
        return f'\033[48;5;{c}m'

    def color(self, c):
        return f'\033[{c}m'

    def update_render_tree(self):
        # TODO: hierarchy update
        for _, (dirty,) in self.get_components(Dirty):
            for r, (room,) in self.get_components(Room):
                self.add_component(r, Dirty())
            for r, (position,) in self.get_components(Position):
                self.add_component(r, Dirty())

    def render(self):
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
                            output.append(self.color_bg(234))
                            output.append(self.mv(x,y,' '))
                            output.append(self.color(SC.RESET))

            for es, (pos, s, dirty) in self.get_components(Position, Style, Dirty):
                is_player_self = ed == es and self.has_component(es, Player)
                output.append(self.color_bg(234))
                if is_player_self:
                    output.append(self.color(C.GREEN))
                output.append(self.mv(pos.x, pos.y, s.icon))
                if is_player_self:
                    output.append(self.color(SC.RESET))

            output.append(self.mv())
            output.append(self.color(SC.RESET))
            nd.q_out.put(''.join(output))

    def finalize(self):
        for r, (dirty,) in self.get_components(Dirty):
            self.remove_component(r, Dirty)

    def process(self):
        self.update_render_tree()
        self.render()
        self.finalize()
