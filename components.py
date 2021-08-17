from dataclasses import dataclass
from queue import Queue

@dataclass
class EnergySource:
    max_capacity: int = 1000
    capacity: float = max_capacity

@dataclass
class EnergySink:
    consumption: int = 1

@dataclass
class Position:
    x: int = 0
    y: int = 0

@dataclass
class Style:
    icon: str = '@'

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
