#!/usr/bin/env python3

from time import sleep

from esper import World

from components import Renderable, Terrain
from network import NetworkThread
from systems import PlayerSystem, RenderSystem, TelnetSystem

world = World()


def main():
    world.add_processor(PlayerSystem())
    world.add_processor(TelnetSystem())
    world.add_processor(RenderSystem())

    world.create_entity(Terrain())
    world.create_entity(Renderable(0,0,fg_char='+'))

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
