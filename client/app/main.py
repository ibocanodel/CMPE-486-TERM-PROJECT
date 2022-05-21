import argparse
import json
import random
from enum import Enum

import pygame

from .hud import InfoBar
from .hero_with_controller import Hero, Vehicle, RoadType
from .world import World
from .input_control import InputControl
from .utils import get_file_name

from .color import *


class SimulationType(Enum):
    noRender, allRender, choose = range(3)


class SelectType(Enum):
    first, random, select, all, none = range(5)


def game_loop(args, sim_no, road_type, render):
    """Initialized, Starts and runs all the needed modules for No Rendering Mode"""
    try:

        # Init Pygame
        pygame.init()
        if render:
            display = pygame.display.set_mode(
                (args.width, args.height), pygame.HWSURFACE | pygame.DOUBLEBUF
            )
            # Place a title to game window
            pygame.display.set_caption(args.description)

            # Show loading screen
            font = pygame.font.Font(pygame.font.get_default_font(), 20)
            text_surface = font.render("Rendering map...", True, COLOR_WHITE)
            display.blit(
                text_surface,
                text_surface.get_rect(center=(args.width / 2, args.height / 2)),
            )
            pygame.display.flip()

        # Init
        hud = InfoBar(args.width, args.height)
        input_control = InputControl()
        world = World(args, render)
        v2 = Hero(Vehicle.V2, road_type, sim_no)
        v1 = Hero(Vehicle.V1, road_type, sim_no)
        hero = Hero(Vehicle.Hero, road_type, sim_no)
        # For each module, assign other modules that are going to be used inside that module
        hud.start(world)
        input_control.start(hud, world)
        world.start(input_control)
        v1_input, v2_input, hero_input = get_files_and_set_speeds(road_type)
        v2.start(world, v2_input)
        v1.start(world, v1_input)
        hero.start(world, hero_input)

        # Game loop
        clock = pygame.time.Clock()
        while True:
            clock.tick_busy_loop(500)

            # Tick all modules
            world.tick(clock)
            v1.tick(clock)
            v2.tick(clock)
            hero.tick(clock)
            hud.tick(clock, hero)
            input_control.tick(clock)

            # Render all modules
            if render:
                display.fill(COLOR_ALUMINIUM_4)
                world.render(display)
                hud.render(display)
                input_control.render(display)

                pygame.display.flip()

    except KeyboardInterrupt:
        print("\nCancelled by user. Bye!")
    except RuntimeError:
        print("\nRuntime Error")
    finally:
        if hero is not None:
            hero.destroy()
        if v1 is not None:
            v1.destroy()
        if v2 is not None:
            v2.destroy()


def get_files_and_set_speeds(road_type):
    v1_input = json.loads(readfile("Inputs/Vehicle1_" + road_type.name + ".json"))
    v2_input = json.loads(readfile("Inputs/Vehicle2_" + road_type.name + ".json"))
    hero_input = json.loads(readfile("Inputs/hero_" + road_type.name + ".json"))
    print("v1 speed")
    v1_speed = getRandomSpeed(70, 90)
    print("v2 speed")
    v2_speed = getRandomSpeed(0, 20)
    print("hero speed")
    hero_speed = getRandomSpeed(70, 90)
    hero_input["spawn"]["x"] = 195 + (5 / 2 * (v1_speed - hero_speed))
    v2_input["spawn"]["x"] = 475 - (v2_speed  * 5)
    v1_input["speed"] = v1_speed
    v2_input["speed"] = v2_speed
    hero_input["speed"] = hero_speed
    return v1_input, v2_input, hero_input


def readfile(path):
    f = open(get_file_name(path), "r")
    lines = [line.rstrip('\n') for line in f.readlines() if line.strip() != '']
    f.close()
    return "".join(lines)


def getSpeed(speed):
    return round(speed * 5 / 18, 2)


def getRandomSpeed(min, max):
    speed = random.uniform(min, max)
    print(speed)
    return round(speed * 5 / 18, 2)


def open_and_write_to_file(file_name, write, format):
    f = open(get_file_name(file_name), format)
    f.write(write)
    f.close()


def parse_sim_options(arg, count):
    list = range(count)
    if arg[0].casefold() == "first".casefold():
        return range(int(arg[1]) + 1)
    elif arg[0].casefold() == "random".casefold():
        return random.sample(list, int(arg[1]))
    elif arg[0].casefold() == "select".casefold():
        list = []
        for i in arg[1:]:
            list.append(int(i))
        print(list)
        return list
    elif arg[0].casefold() == "all".casefold():
        return list
    elif arg[0].casefold() == "none".casefold():
        return []
    else:
        raise Exception("Invalid option")


def parse_sim_type(arg):
    if arg.casefold() == "noRender".casefold():
        return SimulationType.noRender
    elif arg.casefold() == "allrender".casefold():
        return SimulationType.allRender
    elif arg.casefold() == "choose".casefold():
        return SimulationType.choose
    else:
        raise Exception("Invalid simulation type")


def main():
    """Parses the arguments received from commandline and runs the game loop"""

    # Define arguments that will be received and parsed
    argparser = argparse.ArgumentParser()

    argparser.add_argument(
        "--host",
        metavar="H",
        default="127.0.0.1",
        help="IP of the host server (default: 127.0.0.1)",
    )
    argparser.add_argument(
        "-p",
        "--port",
        metavar="P",
        default=2000,
        type=int,
        help="TCP port to listen to (default: 2000)",
    )
    argparser.add_argument(
        "--tm-port",
        metavar="P",
        default=8000,
        type=int,
        help="Port to communicate with TM (default: 8000)",
    )
    argparser.add_argument(
        "--timeout",
        metavar="X",
        default=2.0,
        type=float,
        help="Timeout duration (default: 2.0s)",
    )
    argparser.add_argument(
        "--res",
        metavar="WIDTHxHEIGHT",
        default="1280x720",
        help="window resolution (default: 1280x720)",
    )
    argparser.add_argument(
        "--filter",
        metavar="PATTERN",
        default="vehicle.audi.*",
        help='actor filter (default: "vehicle.audi.*")',
    )
    argparser.add_argument(
        "--simTypeStraight",
        metavar="Display simulations straight",
        default="allRender",
        help='simulation type(noRender,allRender,choose)'
    )
    argparser.add_argument(
        "--simTypeCurved",
        metavar="Display simulations curved",
        default="noRender",
        help='simulation type(noRender,allRender,choose)'
    )
    argparser.add_argument(
        "--sCount",
        type=int,
        default=2,
        help="Number of straight road simulations"
    )
    argparser.add_argument(
        "--cCount",
        type=int,
        default=2,
        help="Number of curved road simulations"
    )
    argparser.add_argument(
        "--straightOpt",
        nargs="*",
        default="random 5",
        help='Three options(first,random,select,all,none)'
    )
    argparser.add_argument(
        "--curvedOpt",
        nargs="*",
        default="random 5",
        help='Three options(first,random,select,all,none)'
    )

    # Parse arguments
    args = argparser.parse_args()
    args.description = "BounCMPE CarlaSim 2D Visualizer"
    args.width, args.height = [int(x) for x in args.res.split("x")]
    sim_type_straight = parse_sim_type(args.simTypeStraight)
    sim_type_curved = parse_sim_type(args.simTypeCurved)
    # Run game loop
    simulation_count_straight = args.sCount
    open_and_write_to_file("accData_Straight.json", "[", "w")
    if sim_type_straight != SimulationType.choose:
        for i in range(simulation_count_straight):
            game_loop(args, i, RoadType.Straight, sim_type_straight == SimulationType.allRender)
    else:
        straight_options = parse_sim_options(args.straightOpt, simulation_count_straight)
        for i in range(simulation_count_straight):
            game_loop(args, i, RoadType.Straight, i in straight_options)
    open_and_write_to_file("accData_Straight.json", "]", "a")
