from dataclasses import dataclass
from functools import lru_cache
from queue import Queue

from euclid import Vector2

class Player:

    __ID: int = 0
    
    def __init__(self):
        self.win_w = 80
        self.win_h  = 24
        self.cam_x = 0
        self.cam_y = 0
        self.cam_dirty = True

        self.win_resized = True

        Player.__ID += 1
        self.id = self.__ID
        self.q_in = Queue()
        self.q_out = Queue()
        self.__buffer = []

    def write(self, data):
        self.__buffer.append(data)
        if len(self.__buffer) > 1024:
            self.flush()

    def flush(self):
        if len(self.__buffer):
            self.q_out.put(''.join(self.__buffer))
            self.__buffer.clear()

    def send(self, data):
        self.flush()
        self.q_out.put(data)

    def recv(self):
        return self.q_in.get()

    def mv_cursor(self, x=0, y=0, text=''):
        x = round(x)
        y = round(y)
        if x < 0 or y < 0:
            self.write('')
        elif x == 0:
            self.write(f'\033[{y+1}H{text}')
        elif y == 0:
            self.write(f'\033[;{x+1}H{text}')
        else:
            self.write(f'\033[{y+1};{x+1}H{text}')

    def cls(self):
        self.write('\033[2J')

    def show_cursor(self):
        self.write('\033[?25h')

    def hide_cursor(self):
        self.write('\033[?25l')

    def color_fg(self, c):
        self.write(f'\033[38;5;{c}m')

    def color_bg(self, c):
        self.write(f'\033[48;5;{c}m')

    def color(self, c):
        self.write(f'\033[{c}m')

    def color_reset(self):
        self.write('\033[0m')

    def bold(self):
        self.write('\033[1m')

    @property
    def has_data(self):
        return not self.q_in.empty()


class Dirtyable:
    def __init__(self):
        self.dirty = True

    def __setattr__(self, name, value):
        if name != 'dirty':
            self.dirty = True
        super(Dirtyable, self).__setattr__(name, value)


@dataclass
class Renderable(Dirtyable):
    w: int = 0
    h: int = 0
    fg_char: str = 'X'
    bg_char: str = ''
    fg_color: int = 7
    bg_color: int = 234
    fg_animation: str = ''
    bg_animation: str = ''
    fg_animation_speed: float = 3
    bg_animation_speed: float = 3
    fg_animation_time: float = 0
    bg_animation_time: float = 0

    # layer?

class Position(Vector2):
    def __init__(self, x, y):
        super().__init__(x=x, y=y)
        self.ox = 0
        self.oy = 0

class Velocity(Vector2):
    pass


class Terrain(Dirtyable):
    SCALE = 0.008
    LOD = 5

    OCEAN = 19
    WATER = 31
    SAND = 222
    SANDGRASS = 178
    GRASS = 22
    GRASS_LIGHT = 28
    ROCK = 240
    SNOW = 255
    

    def __init__(self, seed = 2):
        from opensimplex import OpenSimplex
        self.noise2d_generators = [OpenSimplex(seed + i).noise2d for i in range(self.LOD)]


    @lru_cache(maxsize=4096)
    def get_value(self, x, y):
        v = 0.0
        divisor = 0.0

        nx = x*self.SCALE
        ny = y*self.SCALE

        for i in range(self.LOD):
            f = 2**i
            divisor += 1.0 / f
            v += self.noise2d_generators[i](f*nx, f*ny) / f

        v /= divisor

        return v


    def get(self, x, y):
        return self.get_bg(self.get_value(x,y))


    def get_entity(self, x, y):
        v = self.get_value(x, y)
        bg = self.get_bg(v)
        return bg == self.GRASS_LIGHT and v * self.noise2d_generators[0](x, y) < -0.14


    def get_bg(self, v):
        if v < -0.1:
            b = self.OCEAN
        elif v <= 0:
            b = self.WATER
        elif v < 0.02:
            b = self.SAND
        elif v < 0.15:
            b = self.SANDGRASS
        elif v < 0.3:
            b = self.GRASS_LIGHT
        elif v < 0.46:
            b = self.GRASS
        elif v < 0.52:
            b = self.ROCK
        else:
            b = self.SNOW

        return b


class Connect:
    pass


class Disconnect:
    pass

@dataclass
class Level:
    level: float = 100.0

    def sub(self, v):
        if self.level > 0:
            self.level -= v
        if self.level < 0:
            self.level = 0

    def add(self, v):
        if self.level < 100:
            self.level += v
        if self.level > 100:
            self.level = 100

class Health(Level):
    pass

class Stomach(Level):
    pass

class Hydration(Level):
    pass

class Oxygen(Level):
    pass
