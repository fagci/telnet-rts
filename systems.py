from esper import Processor, World

from components import Connect, Renderable, Disconnect, NetworkData, Player

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
        for e, (nd, pos) in self.get_components(NetworkData, Renderable):
            while not nd.q_in.empty():
                data = nd.q_in.get()
                if data == KeyCodes.UP:
                    pos.y -= 1
                if data == KeyCodes.DOWN:
                    pos.y += 1
                if data == KeyCodes.LEFT:
                    pos.x -= 1
                if data == KeyCodes.RIGHT:
                    pos.x += 1

class PlayerConnectionSystem(System):
    def process(self):
        for e, (src,) in self.get_components(Disconnect):
            # FIXME: render before leave
            self.remove_component(e, Disconnect)
            self.delete_entity(e)

        for e, (src,) in self.get_components(Connect):
            # placeholder
            self.remove_component(e, Connect)

class RenderSystem(System):

    def update_render_tree(self):
        # TODO: hierarchy update
        has_updates = False
        for _, (r,) in self.get_components(Renderable):
            if r.is_dirty:
                has_updates = True
                break
        for _, (r,) in self.get_components(Renderable):
            r.set_dirty()
                

    def render(self):
        for ed, (nd,) in self.get_components(NetworkData):
            output = []
            append = output.append

            for es, (room,) in self.get_components(Renderable):
                append(cls())

                x1, x2 = room.x, room.x + room.w
                y1, y2 = room.y, room.y + room.h

                append(color_bg(room.bg_color))
                is_player_self = ed == es and self.has_component(es, Player)
                if is_player_self:
                    append(color(C.GREEN))
                else:
                    append(color_fg(room.fg_color))

                for x in range(x1, x2 + 1):
                    for y in range(y1, y2 + 1):
                        if x == x1 or x == x2 or y == y1 or y == y2:
                            append(mv_cursor(x, y, room.fg_char))
                            append(color(SC.RESET))
                        elif y > y1 and x > x1 and y < y2 and x < x2:
                            append(mv_cursor(x, y, room.bg_char))

                append(color(SC.RESET))
                room.set_pristine()

            append(mv_cursor())
            nd.q_out.put(''.join(output))

    def finalize(self):
        for r, (dirty,) in self.get_components(Dirty):
            self.remove_component(r, Dirty)

    def process(self):
        self.update_render_tree()
        self.render()
        self.finalize()
