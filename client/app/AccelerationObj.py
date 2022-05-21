class AccelerationObj(object):
    def __init__(self, carAcc, waypoint):
        self.carAccX = carAcc.x
        self.carAccY = carAcc.y
        self.carAccZ = carAcc.z
        self.waypointX = waypoint.transform.location.x
        self.waypointY = waypoint.transform.location.y
        self.waypointZ = waypoint.transform.location.z
        self.waypointPitch = waypoint.transform.rotation.pitch
        self.waypointYaw = waypoint.transform.rotation.yaw
        self.waypointRoll = waypoint.transform.rotation.roll
