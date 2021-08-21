#!/usr/bin/env python3

from components import Terrain
from time import sleep

from esper import World

from prefabs import room, fire
from network import NetworkThread
from systems import (
    TelnetSystem,
    PlayerConnectionSystem,
    RenderSystem,
)

world = World()


def main():
    world.add_processor(TelnetSystem())
    world.add_processor(PlayerConnectionSystem())
    world.add_processor(RenderSystem())

    # world.create_entity(*room())
    world.create_entity(Terrain())
    world.create_entity(*fire(5,5))

    network_thread = NetworkThread(world, '0.0.0.0')
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
