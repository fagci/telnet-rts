from telnetlib import IAC, NAWS, SB
from time import time

from esper import Processor, World

from components import Connect, Disconnect, Player, Renderable, Terrain
from styles import SC, bold, cls, color, color_bg, color_fg, mv_cursor, color_reset

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
    def log(self, *args, **kwargs):
        n = self.__class__.__name__.split('System')[0]
        print(f'[{n}]', *args, **kwargs)

class TelnetSystem(System):
    def process_cmd(self, player, renderable, data):
        for command in data.split(IAC):
            if command.startswith(SB + NAWS):
                player.win_h, player.win_w = unpack('HH', command[6:1:-1])
                renderable.dirty = 1
                self.log(f'w={player.win_w}, h={player.win_h}')


    def process(self):
        for _, (player, renderable) in self.get_components(Player, Renderable):
            while player.has_data:
                data = player.recv()
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


class PlayerSystem(System):
    def process(self):
        for e, (_, player) in self.get_components(Disconnect, Player):
            self.log('-', player.id)
            # FIXME: render before leave
            self.remove_component(e, Disconnect)
            self.delete_entity(e)

        for e, (_, player) in self.get_components(Connect, Player):
            self.log('+', player.id)
            player.send(cls())
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
        for ed, (player, pos) in self.get_components(Player, Renderable):
            for e, (t,) in self.get_components(Terrain):
                terrain = t
                if t.dirty:
                    for x in range(player.win_w):
                        for y in range(player.win_h):
                            player.write(color_bg(t.get(x,y)))
                            player.write(mv_cursor(x,y,' '))
                player.write(color(SC.RESET))
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

                # player.write(color_bg(obj.bg_color))
                is_player_self = ed == es and self.has_component(es, Player)
                if is_player_self:
                    player.write(color_fg(5))
                    player.write(bold())
                else:
                    player.write(color_fg(obj.fg_color))

                for x in range(x1, x2 + 1):
                    for y in range(y1, y2 + 1):
                        player.write(color_bg(terrain.get(x,y)))
                        if x == x1 or x == x2 or y == y1 or y == y2:
                            player.write(mv_cursor(x, y, obj.fg_char))
                            player.write(color_reset())
                        elif y > y1 and x > x1 and y < y2 and x < x2:
                            player.write(mv_cursor(x, y, obj.bg_char))

                player.write(color_reset())
                obj.dirty = False

            for i in range(player.win_h - 5, player.win_h - 1):
                player.write(mv_cursor(1, i, ' '* (player.win_w - 2)))
                
            player.write(mv_cursor(2, player.win_h - 5))
            player.write(f'{player.id}: x={pos.x}, y={pos.y}')

            player.write(mv_cursor())
            player.flush()

    def process(self):
        self.update_render_tree()
        self.render()
