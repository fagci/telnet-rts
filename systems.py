from esper import Processor, World

from components import Connect, Dirty, Disconnect, EnergySink, EnergySource, NetworkData, Player, Position, Room, Style

from styles import C, BC, SC, mv_cursor, cls, color, color_bg, color_fg


class KeyCodes:
    UP = b'\x1b[A'
    RIGHT = b'\x1b[C'
    DOWN = b'\x1b[B'
    LEFT = b'\x1b[D'

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
    def has_component(self, e, c):
        return self.world.has_component(e, c)

class InputHandleSystem(System):
    def process(self):
        for e, (nd, pos) in self.get_components(NetworkData, Position):
            while not nd.q_in.empty():
                data = nd.q_in.get()
                if data == KeyCodes.UP:
                    pos.y -= 1
                    self.add_component(e, Dirty())
                if data == KeyCodes.DOWN:
                    pos.y += 1
                    self.add_component(e, Dirty())
                if data == KeyCodes.LEFT:
                    pos.x -= 1
                    self.add_component(e, Dirty())
                if data == KeyCodes.RIGHT:
                    pos.x += 1
                    self.add_component(e, Dirty())


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
            append = output.append

            for r, (room, dirty) in self.get_components(Room, Dirty):
                append(cls())

                x1, x2 = room.x, room.x + room.w
                y1, y2 = room.y, room.y + room.h

                for x in range(x1, x2 + 1):
                    for y in range(y1, y2 + 1):
                        if x == x1 or x == x2 or y == y1 or y == y2:
                            append(mv_cursor(x, y, '█'))
                        elif y > y1 and x > x1 and y < y2 and x < x2:
                            append(color_bg(234))
                            append(mv_cursor(x, y, ' '))
                            append(color(SC.RESET))

            for es, (pos, s, dirty) in self.get_components(Position, Style, Dirty):
                is_player_self = ed == es and self.has_component(es, Player)
                append(color_bg(234))
                if is_player_self:
                    append(color(C.GREEN))
                append(mv_cursor(pos.x, pos.y, s.icon))
                if is_player_self:
                    append(color(SC.RESET))

            append(mv_cursor())
            append(color(SC.RESET))
            nd.q_out.put(''.join(output))

    def finalize(self):
        for r, (dirty,) in self.get_components(Dirty):
            self.remove_component(r, Dirty)

    def process(self):
        self.update_render_tree()
        self.render()
        self.finalize()
