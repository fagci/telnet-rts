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
        self.q_out.put(data)

    def recv(self):
        return self.q_in.get()

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
    SCALE = 0.01

    OCEAN = 19
    WATER = 31
    SAND = 222
    SANDGRASS = 94
    GRASS = 22
    GRASS_LIGHT = 100
    ROCK = 240
    SNOW = 7
    

    def __init__(self, seed = 0):
        from opensimplex import OpenSimplex
        self.octaves = [OpenSimplex(seed + i) for i in range(5)]


    @lru_cache(10000)
    def get(self, x, y):
        v = 0.0
        divisor = 0.0
        amplitude = 0.5
        nx = (float(x) / (200 * amplitude)) - amplitude
        ny = (float(y) / (200 * amplitude)) - amplitude
        for i, n in enumerate(self.octaves):
            f = 2**i
            divisor += 1.0 / f
            v += n.noise2d(f*nx, f*ny) / f
        v /= divisor

        if v < - 0.1:
            b = self.OCEAN
        elif v < -0.063:
            b = self.WATER
        elif v < 0.02:
            b = self.SAND
        elif v < 0.15:
            b = self.SANDGRASS
        elif v < 0.4:
            b = self.GRASS
        elif v < 0.46:
            b = self.GRASS_LIGHT
        elif v < 0.49:
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
