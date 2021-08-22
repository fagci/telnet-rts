from dataclasses import dataclass
from functools import lru_cache
from queue import Queue

from euclid import Vector2

class Player:
    id: int = 0
    win_w: int = 80
    win_h : int = 24
    cam_x: int = 0
    cam_y: int = 0
    cam_dirty: bool = True

    win_resized: bool = True

    __ID: int = 0
    __buffer: list = []
    
    def __init__(self):
        Player.__ID += 1
        self.id = self.__ID
        self.q_in = Queue()
        self.q_out = Queue()

    def write(self, data):
        self.__buffer.append(data)

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
    dirty: bool = True
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
    ox: int = 0
    oy: int = 0

class Velocity(Vector2):
    pass


class Terrain(Dirtyable):
    SCALE = 0.01

    WATER = 31
    

    def __init__(self):
        from opensimplex import OpenSimplex
        from random import seed
        seed(0)
        self.noise = OpenSimplex()


    @lru_cache(1024)
    def get(self, x, y):
        v = (self.noise.noise2d(x*self.SCALE, y*self.SCALE)+1)/2

        if v > 0.85:
            b = 7
        elif v > 0.7:
            b = 240
        elif v > 0.45:
            b = 70
        elif v > 0.18:
            b = 22
        elif v > 0.15:
            b = 222
        else:
            b = Terrain.WATER

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

