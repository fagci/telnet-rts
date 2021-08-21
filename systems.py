from telnetlib import IAC, NAWS, SB, WILL
from time import time

from esper import Processor, World

from components import Connect, Disconnect, NetworkData, Player, Renderable, Terrain
from styles import SC, cls, color, color_bg, color_fg, mv_cursor, color_reset

from struct import unpack

class KeyCodes:
    UP = b'\x1b[A'
    RIGHT = b'\x1b[C'
    DOWN = b'\x1b[B'
    LEFT = b'\x1b[D'

class System(Processor):
    """Fix types, ease access to methods"""
    world: World
    def get_components(self, *args) -> list:
        return self.world.get_components(*args)
    def remove_component(self, e, c):
        return self.world.remove_component(e, c)
    def add_component(self, e, c):
        return self.world.add_component(e, c)
    def delete_entity(self, e):
        return self.world.delete_entity(e)
    def has_component(self, e, c):
        return self.world.has_component(e, c)

class TelnetSystem(System):
    def process_cmd(self, player, renderable, data):
        for command in data.split(IAC):
            if command.startswith(SB + NAWS):
                player.win_h, player.win_w = unpack('HH', command[6:1:-1])
                renderable.dirty = 1
                print(f'[T] w={player.win_w}, h={player.win_h}')


    def process(self):
        for _, (nd, player, renderable) in self.get_components(NetworkData, Player, Renderable):
            while nd.has_data:
                data = nd.recv()
                if data == KeyCodes.UP:
                    renderable.y -= 1
                elif data == KeyCodes.DOWN:
                    renderable.y += 1
                elif data == KeyCodes.LEFT:
                    renderable.x -= 1
                elif data == KeyCodes.RIGHT:
                    renderable.x += 1
                else:
                    self.process_cmd(player, renderable, data)


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
            if r.dirty:
                has_updates = True
                break
        if has_updates:
            for _, (r,) in self.get_components(Renderable):
                r.dirty = True
                

    def render(self):
        for ed, (player, nd, pos) in self.get_components(Player, NetworkData, Renderable):
            output = []
            append = output.append

            for e, (t,) in self.get_components(Terrain):
                terrain = t
                if t.dirty:
                    for x in range(player.win_w):
                        for y in range(player.win_h):
                            append(color_bg(t.get(x,y)))
                            append(mv_cursor(x,y,' '))
                append(color(SC.RESET))
                t.dirty = False

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


                if not obj.dirty:
                    continue

                x1, x2 = obj.x, obj.x + obj.w
                y1, y2 = obj.y, obj.y + obj.h

                # append(color_bg(obj.bg_color))
                is_player_self = ed == es and self.has_component(es, Player)
                if is_player_self:
                    append(color_fg(5))
                else:
                    append(color_fg(obj.fg_color))

                for x in range(x1, x2 + 1):
                    for y in range(y1, y2 + 1):
                        append(color_bg(terrain.get(x,y)))
                        if x == x1 or x == x2 or y == y1 or y == y2:
                            append(mv_cursor(x, y, obj.fg_char))
                            append(color_reset())
                        elif y > y1 and x > x1 and y < y2 and x < x2:
                            append(mv_cursor(x, y, obj.bg_char))

                append(color_reset())
                obj.dirty = False

            append(mv_cursor(0, 20))
            append(f'{player.id}: x={pos.x}, y={pos.y}')

            append(mv_cursor())
            nd.q_out.put(''.join(output))

    def process(self):
        self.update_render_tree()
        self.render()
