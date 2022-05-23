import argparse
import json
import random
from enum import Enum

import pygame

from .hud import InfoBar
from .Vehicle1 import Vehicle1
from .world import World
from .input_control import InputControl
from .utils import *
from .enums import *
from .color import *
from .Hero import Hero
from .Vehicle2 import Vehicle2





def game_loop(args, sim_no, road_type, render):
    """Initialized, Starts and runs all the needed modules for No Rendering Mode"""
    try:

        # Init Pygame
        pygame.init()
        print("Simulation", sim_no + 1, "for", road_type.name, "road started.")
        if render:
            display = pygame.display.set_mode(
                (args.width, args.height), pygame.HWSURFACE | pygame.DOUBLEBUF
            )
            # Place a title to game window
            pygame.display.set_caption(
                args.description + "(" + road_type.name + " road simulation #" + str(sim_no + 1) + ")")

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
        v2 = Vehicle2(Vehicle.V2, road_type, sim_no)
        v1 = Vehicle1(Vehicle.V1, road_type, sim_no)
        hero = Hero(Vehicle.Hero, road_type, sim_no)
        # For each module, assign other modules that are going to be used inside that module
        hud.start(world)
        input_control.start(hud, world)
        world.start(input_control, sim_no == 0)
        v1_input, v2_input, hero_input = get_files_and_set_speeds(road_type, sim_no)
        v2.start(world, v2_input)
        v1.start(world, v1_input, v2_input["speed"])
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
            hud.tick(clock, v1)
            input_control.tick(clock)

            # Render all modules
            if render:
                display.fill(COLOR_ALUMINIUM_4)
                world.render(display)
                hud.render(display)
                input_control.render(display)

                pygame.display.flip()

    except EndOfRoadException:
        print("Simulation", sim_no + 1, "for", road_type.name, "road ended.")
    finally:
        if hero is not None:
            hero.destroy()
        if v1 is not None:
            v1.destroy()
        if v2 is not None:
            v2.destroy()
        if render:
            pygame.display.quit()
        pygame.quit()


def get_files_and_set_speeds(road_type, simNo):
    v1_input = json.loads(readfile("Inputs/Vehicle1_" + road_type.name + ".json"))
    v2_input = json.loads(readfile("Inputs/Vehicle2_" + road_type.name + ".json"))
    hero_input = json.loads(readfile("Inputs/hero_" + road_type.name + ".json"))
    v1_speed_kmh, v1_speed = getRandomSpeed(70, 90)
    v2_speed_kmh, v2_speed = getRandomSpeed(0, 20)
    hero_speed_kmh, hero_speed = getRandomSpeed(70, 90)
    if road_type == RoadType.Straight:
        hero_input["spawn"]["x"] = 195 + (5 / 2 * (v1_speed - hero_speed))
        v2_input["spawn"]["x"] = 475 - (v2_speed * 5)
    elif road_type == RoadType.Curved:
        v2_input["spawn"]["x"] = v2_input["spawn"]["x"] - (5 - v2_speed) * 5
    v1_input["speed"] = v1_speed
    v2_input["speed"] = v2_speed
    hero_input["speed"] = hero_speed
    if simNo != 0:
        open_and_write_to_file("speedData_" + road_type.name + ".json", "," +
                               json.dumps(SpeedObj(v1_speed_kmh, v2_speed_kmh, hero_speed_kmh).__dict__), "a")
    else:
        open_and_write_to_file("speedData_" + road_type.name + ".json",
                               json.dumps(SpeedObj(v1_speed_kmh, v2_speed_kmh, hero_speed_kmh).__dict__), "a")
    return v1_input, v2_input, hero_input


def getSpeed(speed):
    return round(speed * 5 / 18, 2)


def getRandomSpeed(min, max):
    speed = random.uniform(min, max)
    return speed, round(speed * 5 / 18, 2)


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
        default="noRender",
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
        default=25,
        help="Number of straight road simulations"
    )
    argparser.add_argument(
        "--cCount",
        type=int,
        default=25,
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
    ),
    argparser.add_argument(
        "--straightPlotNumber",
        type=int,
        default=5,
        help='Number of plot points in straight road simulations'
    ),
    argparser.add_argument(
        "--curvedPlotNumber",
        type=int,
        default=5,
        help='Number of plot points in curved road simulations'
    )

    # Parse arguments
    try:
        removeFiles()
        args = argparser.parse_args()
        args.description = "BounCMPE CarlaSim 2D Visualizer"
        args.width, args.height = [int(x) for x in args.res.split("x")]
        sim_type_straight = parse_sim_type(args.simTypeStraight)
        sim_type_curved = parse_sim_type(args.simTypeCurved)
        # Run game loop
        simulation_count_straight = args.sCount
        simulation_count_curved = args.cCount
        straight_plot_count = args.straightPlotNumber
        curved_plot_count = args.curvedPlotNumber
        prepareFiles()
        if sim_type_straight != SimulationType.choose:
            for i in range(simulation_count_straight):
                game_loop(args, i, RoadType.Straight, sim_type_straight == SimulationType.allRender)
        else:
            straight_options = parse_sim_options(args.straightOpt.split(), simulation_count_straight)
            for i in range(simulation_count_straight):
                game_loop(args, i, RoadType.Straight, i in straight_options)

        # Run game loop

        if sim_type_curved != SimulationType.choose:
            for i in range(simulation_count_curved):
                game_loop(args, i, RoadType.Curved, sim_type_curved == SimulationType.allRender)
        else:
            curved_options = parse_sim_options(args.curvedOpt.split(), simulation_count_curved)
            for i in range(simulation_count_curved):
                game_loop(args, i, RoadType.Straight, i in straight_options)
        closeFiles()
        plot_top_n_accs(RoadType.Straight, straight_plot_count, simulation_count_straight)
        plot_top_n_accs(RoadType.Curved, curved_plot_count, simulation_count_curved)
        generate_speed_tables(simulation_count_straight, simulation_count_curved)
        generate_acc_table(simulation_count_straight, simulation_count_curved)
        generateIntroductionFiles(args)
        removeDataFiles()

    except KeyboardInterrupt:
        print("\nCancelled by user. Bye!")
