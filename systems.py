from telnetlib import IAC, NAWS, SB
from time import time

from esper import Processor, World

from components import Connect, Disconnect, Health, Hydration, Player, Position, Renderable, Stomach, Terrain, Velocity
from styles import cls, color_bg, color_fg, hide_cursor, mv_cursor, color_reset, show_cursor

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
    def component_for_entity(self, e, c):
        return self.world.component_for_entity(e, c)
    def components_for_entity(self, e, *c):
        return self.world.components_for_entity(e, *c)
    def log(self, *args, **kwargs):
        n = self.__class__.__name__.split('System')[0]
        print(f'[{n}]', *args, **kwargs)

class TelnetSystem(System):
    def process_cmd(self, player, renderable, data):
        for command in data.split(IAC):
            if command.startswith(SB + NAWS):
                player.win_h, player.win_w = unpack('HH', command[6:1:-1])
                player.win_resized = True
                renderable.dirty = True
                self.log(f'w={player.win_w}, h={player.win_h}')


    def process(self):
        # TODO: check if we want to add Velocity component or keep it all time
        for _, (player, v, r) in self.get_components(Player, Velocity, Renderable):
            while player.has_data:
                data = player.recv()
                if data == KeyCodes.UP:
                    v.y -= 1
                    r.dirty = True
                elif data == KeyCodes.DOWN:
                    v.y += 1
                    r.dirty = True
                elif data == KeyCodes.LEFT:
                    v.x -= 1
                    r.dirty = True
                elif data == KeyCodes.RIGHT:
                    v.x += 1
                    r.dirty = True
                else:
                    self.process_cmd(player, r, data)


class PlayerSystem(System):
    def process(self):
        for e, (_, player) in self.get_components(Disconnect, Player):
            self.log('-', player.id)
            # FIXME: render before leave
            player.send(show_cursor())
            self.remove_component(e, Disconnect)
            self.delete_entity(e)

        for e, (_, player) in self.get_components(Connect, Player):
            self.log('+', player.id)
            player.write(hide_cursor())
            self.remove_component(e, Connect)

class HealthSystem(System):
    def process(self):
        for e, (t,) in self.get_components(Terrain):
            for _, (pos, v, stomach, hydration, health) in self.get_components(Position, Velocity, Stomach, Hydration, Health):
                block = t.get(pos.x, pos.y)

                if block == Terrain.WATER:
                    hydration.add(1)

                if block == Terrain.SNOW: # TODO: add Cold component?
                    stomach.sub(0.01)

                v_f = abs(v)

                stomach.sub(0.01 if v_f else 0.0025)
                hydration.sub(0.03 if v_f else 0.01)
                if stomach.level == 0 or hydration.level == 0:
                    health.sub(0.2)

class MovementSystem(System):
    def process(self):
        for _, (pos,v) in self.get_components(Position,Velocity):
            pos.ox = pos.x
            pos.oy = pos.y
            pos += v
            v.x = 0
            v.y = 0

class RenderSystem(System):
    def update_camera(self, player, pos):
        CAM_MARGIN = 8
        W2 = int(player.win_w / 2)
        H2 = int(player.win_h / 2)

        if pos.x < player.cam_x - W2 + CAM_MARGIN:
            player.cam_x = W2 - CAM_MARGIN + pos.x
            player.cam_dirty = True
        elif pos.x > player.cam_x + W2 - CAM_MARGIN:
            player.cam_x = - W2 + CAM_MARGIN + pos.x
            player.cam_dirty = True

        if pos.y < player.cam_y - H2 + CAM_MARGIN:
            player.cam_y = H2 - CAM_MARGIN + pos.y
            player.cam_dirty = True
        elif pos.y > player.cam_y + H2 - CAM_MARGIN:
            player.cam_y = - H2 + CAM_MARGIN + pos.y
            player.cam_dirty = True

        self.mx = player.cam_x - int(player.win_w/2)
        self.my = player.cam_y - int(player.win_h/2)

    def draw_terrain(self, player):
        for _, (t,) in self.get_components(Terrain):
            last_c = None

            player.write(mv_cursor())
            for y in range(player.win_h):
                for x in range(player.win_w):
                    c = t.get(x+self.mx, y+self.my)
                    if c != last_c:
                        player.write(color_bg(c))
                        last_c = c
                    player.write(' ')
            player.flush()


    def render(self):
        # draw terrain for each player
        for ed, (player, player_pos) in self.get_components(Player, Position):
            if player.win_resized:
                player.write(cls())
                player.cam_x = player_pos.x
                player.cam_y = player_pos.y

            self.update_camera(player, player_pos)

            if player.win_resized or player.cam_dirty:
                self.draw_terrain(player)

        # animate renderables
        # for _, (renderable) in self.get_components(Renderable):
        #     self.animate(renderable)

        # to get terrain bg color
        for _, (terrain,) in self.get_components(Terrain):
            # draw renderables for each player
            for obj_id, (pos, renderable) in self.get_components(Position, Renderable):
                if not renderable.dirty:
                    continue

                ox, oy = pos.ox - self.mx, pos.oy - self.my
                x, y = pos.x - self.mx, pos.y - self.my
                # FIXME: another player draws wrong terrain bg
                terrain_obg = terrain.get(pos.ox, pos.oy)
                terrain_bg = terrain.get(pos.x, pos.y)

                for player_id, (player, player_pos) in self.get_components(Player, Position):
                    # draw objects only visible to player
                    if x < 0 or y < 0 or x > player.win_w or y > player.win_h:
                        continue

                    is_player_self = obj_id == player_id

                    # clear old pos with terrain color
                    player.write(color_bg(terrain_obg))
                    player.write(mv_cursor(ox, oy, ' '))
                    
                    player.write(color_bg(terrain_bg))
                    player.write(color_fg(1 if is_player_self else renderable.fg_color))

                    player.write(mv_cursor(x, y, renderable.fg_char))

                renderable.dirty = False

        for ed, (player, player_pos) in self.get_components(Player, Position):
            self.draw_ui(ed, player, player_pos)

        # reset cursor position & writeout buffer
        for ed, (player,) in self.get_components(Player):
            player.write(mv_cursor())
            player.flush()
            player.win_resized = False
            player.cam_dirty = False

    def draw_ui(self, ed, player, player_pos):
        stomach = self.component_for_entity(ed, Stomach)
        hydration = self.component_for_entity(ed, Hydration)
        health = self.component_for_entity(ed, Health)

        player.write(color_reset())

        player.write(mv_cursor(2, player.id))
        player.write(f'Player {player.id}')
        
        for i in range(player.win_h - 6, player.win_h - 1):
            player.write(mv_cursor(1, i, ' '*(player.win_w - 2)))
        
        player.write(mv_cursor(2, player.win_h - 5))
        player.write(f'W: {player.win_w} x {player.win_h}')
        player.write(mv_cursor(2, player.win_h - 4))
        player.write(f'CAM: {player.cam_x},{player.cam_y}')
        player.write(mv_cursor(2, player.win_h - 3))
        player.write(f'POS: {player_pos.x},{player_pos.y}')

        player.write(mv_cursor(player.win_w-12, player.win_h-5))
        player.write('S'*round(stomach.level/10))
        player.write(mv_cursor(player.win_w-12, player.win_h-4))
        player.write('H'*round(hydration.level/10))
        player.write(mv_cursor(player.win_w-12, player.win_h-3))
        player.write('♡'*round(health.level/10))
        


    def animate(self, renderable):
        t = time()

        if renderable.fg_animation and (t - renderable.fg_animation_time > 1 / renderable.fg_animation_speed):
            animation_length = len(renderable.fg_animation)
            current_animation_idx = renderable.fg_animation.find(renderable.fg_char)
            renderable.fg_char = renderable.fg_animation[(current_animation_idx+1) % animation_length]
            renderable.fg_animation_time = t

        if renderable.bg_animation and (t - renderable.bg_animation_time > 1 / renderable.bg_animation_speed):
            animation_length = len(renderable.bg_animation)
            current_animation_idx = renderable.bg_animation.find(renderable.bg_char)
            renderable.bg_char = renderable.bg_animation[(current_animation_idx+1) % animation_length]
            renderable.bg_animation_time = t

    def process(self):
        self.render()
