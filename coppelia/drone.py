from dcs_world.robot.drone import Drone
from dcs_world.communication import Subscriber, Publisher
from dcs_world.geometry import Twist, Pose
from dcs_world.communication.messages import RobotStatusMessage
from dcs_world.coppelia.utils import get_next_drone_id

import time

COMMAND_TIMEOUT = 0.5

def set_target_pose(pose, target_handle):
    sim.setObjectPosition(
        target_handle, -1, [pose.x, pose.y, pose.z]
    )
    sim.setObjectOrientation(
        target_handle, -1, [0.0, 0.0, pose.yaw]
    )


def on_cmd_vel(message):
    self.cmd_vel = message
    self.last_cmd_time = time.monotonic()


def sysCall_init():
    sim = require('sim')

    self.drone_handle = sim.getObject('/Quadcopter')
    self.target_handle = sim.getObject('/target')

    robot_id = get_next_drone_id(sim)

    position = sim.getObjectPosition(self.drone_handle, -1)
    orientation = sim.getObjectOrientation(self.drone_handle, -1)

    init_pose = Pose.from_coordinates(
        x=position[0],
        y=position[1],
        z=position[2],
        yaw=orientation[2]
    )

    self.drone = Drone(
        id=str(robot_id),
        init_pose=init_pose,
        init_soc=100.0,
        config=Drone.DEFAULT_CONFIG
    )

    self.dt = sim.getSimulationTimeStep()

    # Initial command: zero velocity
    self.cmd_vel = Twist(
        linear=[0.0, 0.0, 0.0],
        angular=[0.0, 0.0, 0.0]
    )

    self.last_cmd_time = time.monotonic()

    # Subscribe to velocity commands
    self.cmd_vel_sub = Subscriber(
        topic=f"{self.drone.id}.cmd_vel",
        message_type=Twist,
        callback=on_cmd_vel
    )

    # Status publisher
    self.status_pub = Publisher(
        topic=f"{self.drone.id}.status"
    )


def sysCall_actuation():
    # Receive pending commands
    self.cmd_vel_sub.receive()

    # Stop if no command has arrived recently
    if time.monotonic() - self.last_cmd_time > COMMAND_TIMEOUT:
        self.cmd_vel = Twist(
            linear=[0.0, 0.0, 0.0],
            angular=[0.0, 0.0, 0.0]
        )

    self.drone.move(self.cmd_vel, self.dt)

    set_target_pose(self.drone.pose, self.target_handle)

    self.status_pub.publish(
        RobotStatusMessage.from_robot(self.drone)
    )


def sysCall_sensing():
    pass


def sysCall_cleanup():
    self.cmd_vel_sub.close()
    self.status_pub.close()