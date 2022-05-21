import json
from enum import Enum

import carla

from .controller import PurePursuitController
from .AccelerationObj import AccelerationObj
from .utils import get_file_name
import numpy as np


class Vehicle(Enum):
    V1, V2, Hero = range(3)


class RoadType(Enum):
    Straight, Curved = range(2)


class Hero(object):
    def __init__(self, vehicleType, RoadType, simNo):
        self.world = None
        self.actor = None
        self.control = None
        self.controller = None
        self.waypoints = []
        self.target_speed = None  # meters per second
        self.accs = []
        self.vehicleType = vehicleType
        self.roadType = RoadType
        self.simNo = simNo

    def start(self, world, input):

        self.world = world
        spawn_point = carla.Transform(
            carla.Location(x=input["spawn"]["x"], y=input["spawn"]["y"], z=input["spawn"]["z"]), carla.Rotation(yaw=input["spawn"]["yaw"]))

        self.actor = self.world.spawn_hero("vehicle.audi.tt", spawn_point)

        self.waypoints = self.get_waypoints(input["waypoints"])

        self.target_speed = input["speed"]  # meters per second
        self.controller = PurePursuitController()

        self.world.register_actor_waypoints_to_draw(self.actor, self.waypoints)
        # self.actor.set_autopilot(True, world.args.tm_port)

    def tick(self, clock):

        throttle, steer = self.controller.get_control(
            self.actor,
            self.waypoints,
            self.target_speed,
            self.world.fixed_delta_seconds,
        )
        ctrl = carla.VehicleControl()
        ctrl.throttle = throttle
        ctrl.steer = steer
        self.actor.apply_control(ctrl)
        if self.vehicleType == Vehicle.V1:
            self.accs.append(
                self.calc_acc(self.actor.get_acceleration(),
                              self.world.town_map.get_waypoint(self.actor.get_location()))[1])

    def destroy(self):
        """Destroy the hero actor when class instance is destroyed"""
        if self.vehicleType == Vehicle.V1:
            self.appendJson("accData_" + self.roadType.name + ".json")
            if self.actor is not None:
                self.actor.destroy()

    def appendJson(self, fileName):
        f = open(get_file_name(fileName), "a")
        if self.simNo != 0:
            f.write(",")
        f.write(json.dumps([ob for ob in self.accs]))

        f.close()

    def get_waypoints(self, waypoints):
        list = []
        for loc in waypoints:
            list.append(carla.Location(loc["x"], loc["y"], loc["z"]))
        return list

    def calc_acc(self, acc_vector, waypoint):
        p = waypoint.transform.location
        r = waypoint.transform.rotation
        theta = np.radians(r.yaw)
        c, s = np.cos(theta), np.sin(theta)
        R = np.array(((c, -s), (s, c)))  # Rotation matrix

        point = np.matmul(np.array([acc_vector.x , acc_vector.y ]), R)

        return point
