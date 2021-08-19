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

class Dirtyable:
    _dirty: bool = True
    def __setattr__(self, name, value):
        if name != '_dirty':
            super().__setattr__(name, value)
            self._dirty = True

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
    w: int
    h: int
    fg_char: str = 'X'
    bg_char: str = ''
    fg_color: int = 7
    bg_color: int = 234
    # layer?


class Connect:
    pass

class Disconnect:
    pass

