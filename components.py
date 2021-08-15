from dataclasses import dataclass

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
