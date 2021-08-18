#!/usr/bin/env python3

from time import sleep

from esper import World

from components import Dirty, Position, Room, Style
from network import NetworkThread
from systems import EnergySystem, RenderSystem, PlayerConnectionSystem

world = World()


def main():
    world.add_processor(EnergySystem())
    world.add_processor(PlayerConnectionSystem())
    world.add_processor(RenderSystem())

    world.create_entity(Room(), Dirty())
    world.create_entity(Position(3,3), Style('O'))
    world.create_entity(Position(6,6), Style('O'))

    network_thread = NetworkThread(world)
    network_thread.setDaemon(True)
    network_thread.start()
    print('server listening')

    try:
        while True:
            world.process()
            sleep(0.05)
    except KeyboardInterrupt:
        print('exit')
        exit(130)

if __name__ == '__main__':
    main()
