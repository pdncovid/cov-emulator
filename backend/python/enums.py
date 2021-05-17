# def enum(*sequential, **named):
#     enums = dict(zip(sequential, range(len(sequential))), **named)
#     return type('Enum', (), enums)

from enum import Enum

Mobility = Enum('Mobility', "RANDOM BROWNIAN")
State = Enum('State', "SUSCEPTIBLE INFECTED RECOVERED")
Shape = Enum('Shape', "POLYGON CIRCLE")
TestSpawn = Enum('Test center spawning method', 'RANDOM HEATMAP')
