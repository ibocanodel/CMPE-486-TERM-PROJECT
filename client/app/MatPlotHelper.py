import json

from matplotlib.ticker import MaxNLocator

from .enums import *
from .utils import *
import matplotlib.pyplot as plt
import numpy as np


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
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
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


def get_y(acc):
    return abs(acc["y"])


def get_top_acc(acc_data):
    acc_data.sort(key=get_y, reverse=True)
    return acc_data[0]["y"]
