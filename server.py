#!/usr/bin/env python3

from components import Position, Style
from time import sleep

from esper import World

from systems import EnergySystem, RenderSystem

world = World()

def main():
    world.add_processor(EnergySystem())
    world.add_processor(RenderSystem())

    world.create_entity(Position(), Style())

    while True:
        world.process()
        sleep(0.05)

if __name__ == '__main__':
    main()
