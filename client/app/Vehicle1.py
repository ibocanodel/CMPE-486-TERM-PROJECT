import json
from enum import Enum

import carla

from .controller import PurePursuitController
from .AccelerationObj import AccelerationObj
from .utils import *
import numpy as np
from .enums import *


class Vehicle1(object):
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
        self.v2STargetSpeed = 0
        self.road_adjusted = False
        self.hero_autopilot = False
        self.turnPoint = None
        self.relative_points = []
        self.spawn_rotation = 0

    def start(self, world, input, v2Speed):
        self.v2STargetSpeed = v2Speed
        self.world = world
        spawn_point = carla.Transform(
            carla.Location(x=input["spawn"]["x"], y=input["spawn"]["y"], z=input["spawn"]["z"]),
            carla.Rotation(yaw=input["spawn"]["yaw"]))
        self.spawn_rotation = input["spawn"]["yaw"]
        self.world.v1Vehicle = self
        self.actor = self.world.spawn_hero("vehicle.audi.tt", spawn_point, self.vehicleType)

        self.waypoints = get_waypoints(input["waypoints"])

        self.target_speed = input["speed"]  # meters per second
        self.controller = PurePursuitController()

        # self.world.register_actor_waypoints_to_draw(self.actor, self.waypoints)
        # self.actor.set_autopilot(True, world.args.tm_port)

    def tick(self, clock):

        throttle, steer, self.relative_points = self.controller.get_control(
            self.actor,
            self.waypoints,
            self.target_speed,
            self.world.fixed_delta_seconds,
        )
        ctrl = carla.VehicleControl()
        ctrl.throttle = throttle
        ctrl.steer = steer
        self.actor.apply_control(ctrl)
        self.accs.append(
            self.calc_acc(self.actor.get_acceleration(),
                          self.world.town_map.get_waypoint(self.actor.get_location())))
        if not self.road_adjusted and get_location_difference(self.actor.get_location(),
                                                              self.world.v2Vehicle.actor.get_location()) <= 2 * (
                self.target_speed - self.v2STargetSpeed):
            self.correct_waypoints()
        elif self.road_adjusted and not self.hero_autopilot and not self.check_loc_inside_waypoints():
            self.hero_autopilot = True
            self.world.heroVehicle.set_autopilot()

    def destroy(self):
        """Destroy the hero actor when class instance is destroyed"""
        if self.vehicleType == Vehicle.V1:
            self.appendJson("accData_" + self.roadType.name + ".json")
            if self.actor is not None:
                self.actor.destroy()

    def check_loc_inside_waypoints(self):

        return any(point.x == self.turnPoint.x for point in self.relative_points)

    def correct_waypoints(self):
        x = self.waypoints[0].x
        loc = self.actor.get_location()
        straight = self.roadType == RoadType.Straight
        self.waypoints = [
            carla.Location(waypoint.x, waypoint.y - 3, waypoint.z) if straight else carla.Location(waypoint.x,
                                                                                                   waypoint.y + 3,
                                                                                                   waypoint.z) for
            waypoint in self.waypoints]
        locPoint = carla.Location(loc.x + 15, self.waypoints[0].y, 0.3) if straight else carla.Location(loc.x - 15,
                                                                                                        self.waypoints[
                                                                                                            0].y, 0.3)
        self.waypoints.append(locPoint)
        self.waypoints.sort(key=self.get_x, reverse=not straight)
        # self.world.register_actor_waypoints_to_draw(self.actor, self.waypoints)
        self.turnPoint = locPoint
        self.road_adjusted = True

    def get_x(self, t):
        return t.x

    def appendJson(self, fileName):
        f = open(get_file_name(fileName), "a")
        if self.simNo != 0:
            f.write(",")
        f.write(json.dumps([ob.__dict__ for ob in self.accs]))

        f.close()

    def calc_acc(self, acc_vector, waypoint):
        p = waypoint.transform.location
        r = waypoint.transform.rotation
        theta = np.radians(r.yaw)
        c, s = np.cos(theta), np.sin(theta)
        R = np.array(((c, -s), (s, c)))  # Rotation matrix

        point = np.matmul(np.array([acc_vector.x, acc_vector.y]), R)

        return AccelerationObj(point)
