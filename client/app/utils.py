import json
import math
import os.path
from pathlib import Path

import carla
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

from .enums import *


def removeFile(path):
    if os.path.exists(path):
        os.remove(path)


def removeFiles():
    removeFile(get_file_name(get_file_name_upper("docs/curved_int.md")))
    removeFile(get_file_name(get_file_name_upper("docs/curved_acc.md")))
    removeFile(get_file_name(get_file_name_upper("docs/curved_speed.md")))
    removeFile(get_file_name(get_file_name_upper("docs/plot_Curved.png")))
    removeFile(get_file_name(get_file_name_upper("docs/plot_Straight.png")))
    removeFile(get_file_name(get_file_name_upper("docs/straight_acc.md")))
    removeFile(get_file_name(get_file_name_upper("docs/straight_int.md")))
    removeFile(get_file_name(get_file_name_upper("docs/straight_speed.md")))
    removeDataFiles()


def prepareFiles():
    open_and_write_to_file("accData_Straight.json", "[", "w")
    open_and_write_to_file("speedData_Straight.json", "[", "w")
    open_and_write_to_file("accData_Curved.json", "[", "w")
    open_and_write_to_file("speedData_Curved.json", "[", "w")


def closeFiles():
    open_and_write_to_file("accData_Straight.json", "]", "a")
    open_and_write_to_file("speedData_Straight.json", "]", "a")
    open_and_write_to_file("accData_Curved.json", "]", "a")
    open_and_write_to_file("speedData_Curved.json", "]", "a")


def removeDataFiles():
    removeFile(get_file_name(get_file_name_upper("client/accData_Curved.json")))
    removeFile(get_file_name(get_file_name_upper("client/accData_Straight.json")))
    removeFile(get_file_name(get_file_name_upper("client/speedData_Curved.json")))
    removeFile(get_file_name(get_file_name_upper("client/speedData_Straight.json")))


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def get_project_root_root() -> Path:
    return Path(__file__).parent.parent.parent


def get_file_name(file_name):
    return os.path.join(get_project_root(), file_name)


def get_file_name_upper(file_name):
    return os.path.join(get_project_root_root(), file_name)


def get_waypoints(waypoints):
    list = []
    for loc in waypoints:
        list.append(carla.Location(loc["x"], loc["y"], loc["z"]))
    return list


def get_location_difference(loc1, loc2):
    return math.sqrt(math.pow(loc1.x - loc2.x, 2) + math.pow(loc1.y - loc2.y, 2))


def readfile(path):
    f = open(get_file_name(path), "r")
    lines = [line.rstrip('\n') for line in f.readlines() if line.strip() != '']
    f.close()
    return "".join(lines)


def open_and_write_to_file(file_name, write, format):
    f = open(get_file_name(file_name), format)
    f.write(write)
    f.close()


def open_and_write_to_file_start_upper(file_name, write, format):
    f = open(get_file_name_upper(file_name), format)
    f.write(write)
    f.close()


class EndOfRoadException(Exception):
    pass


class SpeedObj(object):
    def __init__(self, v1, v2, hero):
        self.v1 = v1
        self.v2 = v2
        self.hero = hero


def generate_speed_tables(simulation_count_straight, simulation_count_curved):
    tableData = json.loads(readfile("speedData_Straight.json"))
    str = "## Straight road simulation speed data\n\n"
    str += "|SimulationNumber|V1 Speed|V2 Speed | Hero Speed \n"
    str += "|---|---|---|---|\n"
    for i in range(simulation_count_straight):
        str += get_table_row_speed(tableData[i], i)
    open_and_write_to_file_start_upper("docs/straight_speed.md", str, "w")
    tableData = json.loads(readfile("speedData_Curved.json"))
    str = "## Curved road simulation speed data\n\n"
    str += "|SimulationNumber|V1 Speed|V2 Speed | Hero Speed \n"
    str += "|---|---|---|---|\n"
    for i in range(simulation_count_curved):
        str += get_table_row_speed(tableData[i], i + 1)
    open_and_write_to_file_start_upper("docs/curved_speed.md", str, "w")


def generate_acc_table(simulation_count_straight, simulation_count_curved):
    data = sort_accs(RoadType.Straight, simulation_count_straight)
    data.sort(key=get_simNo)
    str = "## Straight road simulation acc data\n\n"
    str += "|SimulationNumber|Max acc| \n"
    str += "|---|---|\n"
    for i in range(simulation_count_straight):
        str += get_table_row_acc(data[i], i)
    open_and_write_to_file_start_upper("docs/straight_acc.md", str, "w")
    data = sort_accs(RoadType.Curved, simulation_count_curved)
    str = "## Curved road simulation acc data\n\n"
    str += "|SimulationNumber|Max acc| \n"
    str += "|---|---|\n"
    for i in range(simulation_count_curved):
        str += get_table_row_acc(data[i], i)
    open_and_write_to_file_start_upper("docs/curved_acc.md", str, "w")


def generateIntroductionFiles(args):
    sim_type_straight = parse_sim_type(args.simTypeStraight)
    sim_type_curved = parse_sim_type(args.simTypeCurved)
    mstr = "## Straight road simulation parameters \n\n"
    mstr += "* Simulation count:"
    mstr += str(args.sCount) + "\n"
    mstr += "* Simulation type:" + sim_type_straight.name + "\n"
    if sim_type_straight == SimulationType.choose:
        str1 = ""
        str1.join(parse_sim_options(args.straightOpt.split(), args.sCount))
        mstr += "* Sim Detail:" + str1 + "\n"
    mstr += "* Plotted point count:" + str(args.straightPlotNumber)
    open_and_write_to_file_start_upper("docs/straight_int.md", mstr, "w")
    mstr = "## Curved road simulation parameters \n\n"
    mstr += "* Simulation count:"
    mstr += str(args.cCount) + "\n"
    mstr += "* Simulation type:" + sim_type_curved.name + "\n"
    if sim_type_curved == SimulationType.choose:
        str1 = ""
        str1.join(parse_sim_options(args.curvedOpt.split(), args.sCount))
        mstr += "* Sim Detail:" + str1 + "\n"
    mstr += "* Plotted point count:" + str(args.curvedPlotNumber)
    open_and_write_to_file_start_upper("docs/curved_int.md", mstr, "w")


def get_table_row_acc(data, i):
    mstr = "|"
    mstr += str(data.simNo)
    mstr += "|"
    mstr += str(data.acc)
    mstr += "|\n"
    return mstr


def get_table_row_speed(data, i):
    mstr = "|"
    mstr += str(i)
    mstr += "|"
    mstr += str(data["v1"])
    mstr += "|"
    mstr += str(data["v2"])
    mstr += "|"
    mstr += str(data["hero"])
    mstr += "|\n"
    return mstr


class PlotData(object):
    def __init__(self, simNo, acc):
        self.simNo = simNo
        self.acc = acc


def plot_top_n_accs(road_type, top_n, sim_count):
    data = sort_accs(road_type, sim_count)
    ax = plt.gca()
    plt.scatter([d.simNo for d in data[0:top_n]], [d.acc for d in data[0:top_n]])
    plt.xlabel("Sim Number")
    plt.ylabel("Acceleration (m/s)")
    plt.savefig("docs/plot_" + road_type.name + ".png")


def sort_accs(road_type, sim_count):
    accs = json.loads(readfile("accData_" + road_type.name + ".json"))
    data = []
    for i in range(sim_count):
        t = get_top_acc(accs[i])
        data.append(PlotData(i + 1, abs(t)))
    data.sort(key=get_acc, reverse=True)
    return data


def get_acc(data):
    return data.acc


def get_simNo(data):
    return data.simNo


def get_y(acc):
    return abs(acc["y"])


def get_top_acc(acc_data):
    acc_data.sort(key=get_y, reverse=True)
    return acc_data[0]["y"]


def parse_sim_options(arg, count):
    list = range(count)
    if arg[0].casefold() == "first".casefold():
        return range(int(arg[1]))
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
