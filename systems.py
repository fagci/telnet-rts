from time import time

from esper import Processor, World

from components import Connect, Disconnect, NetworkData, Player, Renderable, Terrain
from styles import BC, C, SC, cls, color, color_bg, color_fg, mv_cursor

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
        for _, (nd, pos) in self.get_components(NetworkData, Renderable):
            while nd.has_data:
                data = nd.recv()
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
        for e, (_,) in self.get_components(Disconnect):
            # FIXME: render before leave
            self.remove_component(e, Disconnect)
            self.delete_entity(e)

        for e, (_, nd) in self.get_components(Connect, NetworkData):
            nd.q_out.put(cls())
            self.remove_component(e, Connect)

class RenderSystem(System):

    def update_render_tree(self):
        # TODO: hierarchy update
        has_updates = False
        for _, (r,) in self.get_components(Renderable):
            if r.is_dirty:
                has_updates = True
                break
        if has_updates:
            for _, (r,) in self.get_components(Renderable):
                r.set_dirty()
                

    def render(self):
        for ed, (nd,) in self.get_components(NetworkData):
            output = []
            append = output.append

            terrain = None

            for e, (t,) in self.get_components(Terrain):
                terrain = t
                if t.is_dirty:
                    for x in range(80):
                        for y in range(24):
                            append(color_bg(t.get(x,y)))
                            append(mv_cursor(x,y,' '))
                append(color(SC.RESET))
                t.set_pristine()

            for es, (obj,) in self.get_components(Renderable):

                t = time()

                if obj.fg_animation and (t - obj.fg_animation_time > 1 / obj.fg_animation_speed):
                    animation_length = len(obj.fg_animation)
                    current_animation_idx = obj.fg_animation.find(obj.fg_char)
                    obj.fg_char = obj.fg_animation[(current_animation_idx+1) % animation_length]
                    obj.fg_animation_time = t

                if obj.bg_animation and (t - obj.bg_animation_time > 1 / obj.bg_animation_speed):
                    animation_length = len(obj.bg_animation)
                    current_animation_idx = obj.bg_animation.find(obj.bg_char)
                    obj.bg_char = obj.bg_animation[(current_animation_idx+1) % animation_length]
                    obj.bg_animation_time = t


                if not obj.is_dirty:
                    continue

                x1, x2 = obj.x, obj.x + obj.w
                y1, y2 = obj.y, obj.y + obj.h

                # append(color_bg(obj.bg_color))
                is_player_self = ed == es and self.has_component(es, Player)
                if is_player_self:
                    append(color(C.GREEN))
                else:
                    append(color_fg(obj.fg_color))

                for x in range(x1, x2 + 1):
                    for y in range(y1, y2 + 1):
                        append(color_bg(terrain.get(x,y)))
                        if x == x1 or x == x2 or y == y1 or y == y2:
                            append(mv_cursor(x, y, obj.fg_char))
                            append(color(SC.RESET))
                        elif y > y1 and x > x1 and y < y2 and x < x2:
                            append(mv_cursor(x, y, obj.bg_char))

                append(color(SC.RESET))
                obj.set_pristine()

            append(mv_cursor())
            nd.q_out.put(''.join(output))

    def process(self):
        self.update_render_tree()
        self.render()
