#!/usr/bin/env python3

from time import sleep

from esper import World

from components import Position, Style
from network import NetworkThread
from systems import EnergySystem, RenderSystem

world = World()


def main():
    world.add_processor(EnergySystem())
    world.add_processor(RenderSystem())

    world.create_entity(Position(3,3), Style('⚑'))
    world.create_entity(Position(6,6), Style('★'))

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
