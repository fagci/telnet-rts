#!/usr/bin/env python3

from queue import Queue
from time import sleep

from esper import World

from components import Position, Style
from network2 import NetworkThread
from systems import EnergySystem, RenderSystem

world = World()


def main():
    net_q_in = Queue()
    net_q_out = Queue()

    world.add_processor(EnergySystem())
    world.add_processor(RenderSystem(net_q_in, net_q_out))

    world.create_entity(Position(), Style())

    network_thread = NetworkThread(world, net_q_in, net_q_out)
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
