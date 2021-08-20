from dataclasses import dataclass
from queue import Queue

@dataclass
class Player:
    id: int = 0
    __ID: int = 0
    def __init__(self):
        Player.__ID += 1
        self.id = self.__ID

class NetworkData:
    def __init__(self):
        self.q_in = Queue()
        self.q_out = Queue()

    def send(self, data):
        self.q_out.put(data)

    def recv(self):
        return self.q_in.get()

    @property
    def has_data(self):
        return not self.q_in.empty()

class Dirtyable:
    _dirty: bool = True
    def __setattr__(self, name, value):
        if name != '_dirty':
            self._dirty = True
        super(Dirtyable, self).__setattr__(name, value)

    def set_pristine(self):
        self._dirty = False

    def set_dirty(self):
        self._dirty = True

    @property
    def is_dirty(self):
        return self._dirty

@dataclass
class Renderable(Dirtyable):
    x: int
    y: int
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


class Connect:
    pass

class Disconnect:
    pass

