from enum import Enum


class Vehicle(Enum):
    V1, V2, Hero = range(3)


class RoadType(Enum):
    Straight, Curved = range(2)


class SimulationType(Enum):
    noRender, allRender, choose = range(3)


class SelectType(Enum):
    first, random, select, all, none = range(5)
