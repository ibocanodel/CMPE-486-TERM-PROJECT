import json
from enum import Enum

import carla

from .controller import PurePursuitController
from .AccelerationObj import AccelerationObj
from .utils import *
import numpy as np
from .enums import *


class Vehicle2(object):
    def __init__(self, vehicleType, RoadType, simNo):
        self.world = None
        self.actor = None
        self.control = None
        self.controller = None
        self.waypoints = []
        self.target_speed = None  # meters per second
        self.vehicleType = vehicleType
        self.roadType = RoadType
        self.simNo = simNo

    def start(self, world, input):

        self.world = world
        spawn_point = carla.Transform(
            carla.Location(x=input["spawn"]["x"], y=input["spawn"]["y"], z=input["spawn"]["z"]),
            carla.Rotation(yaw=input["spawn"]["yaw"]))

        self.actor = self.world.spawn_hero("vehicle.audi.tt", spawn_point, self.vehicleType)
        self.world.v2Vehicle = self
        self.waypoints = get_waypoints(input["waypoints"])

        self.target_speed = input["speed"]  # meters per second
        self.controller = PurePursuitController()

        #self.world.register_actor_waypoints_to_draw(self.actor, self.waypoints)
        # self.actor.set_autopilot(True, world.args.tm_port)

    def tick(self, clock):

        throttle, steer ,points_ahead = self.controller.get_control(
            self.actor,
            self.waypoints,
            self.target_speed,
            self.world.fixed_delta_seconds,
        )
        ctrl = carla.VehicleControl()
        ctrl.throttle = throttle
        ctrl.steer = steer
        self.actor.apply_control(ctrl)

    def destroy(self):
        """Destroy the hero actor when class instance is destroyed"""
        if self.vehicleType == Vehicle.V1:
            self.appendJson("accData_" + self.roadType.name + ".json")
            if self.actor is not None:
                self.actor.destroy()
