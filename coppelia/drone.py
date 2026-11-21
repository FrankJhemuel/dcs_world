from dcs_world.robot.drone import Drone
from dcs_world.communication import Subscriber, Publisher
from dcs_world.geometry import Twist, Pose
from dcs_world.communication.messages import (
    RobotStatusMessage,
    RobotActivationMessage,
    RobotDeactivationMessage
)
from dcs_world.coppelia.utils import get_next_drone_id

import time


# ============================================================
# CONFIGURATION
# ============================================================

COMMAND_TIMEOUT = 0.5

ZERO_TWIST = Twist(
    linear=[0.0, 0.0, 0.0],
    angular=[0.0, 0.0, 0.0]
)


# ============================================================
# POSE
# ============================================================

def set_target_pose(pose, target_handle):

    sim.setObjectPosition(
        target_handle,
        -1,
        [pose.x, pose.y, pose.z]
    )

    sim.setObjectOrientation(
        target_handle,
        -1,
        [0.0, 0.0, pose.yaw]
    )


# ============================================================
# CALLBACKS
# ============================================================

def on_cmd_vel(msg):

    if not self.active:
        return

    self.cmd_vel = msg
    self.last_cmd_time = time.monotonic()


def on_reset_pose(msg: Pose):

    self.drone.reset_pose(msg)

    self.cmd_vel = ZERO_TWIST
    self.last_cmd_time = time.monotonic()

    set_target_pose(
        self.drone.pose,
        self.target_handle
    )


def on_activate(msg):

    self.active = True

    self.cmd_vel = ZERO_TWIST
    self.last_cmd_time = time.monotonic()

    print(f"[Drone] {self.drone.id} activated.")


def on_deactivate(msg):

    self.active = False

    self.cmd_vel = ZERO_TWIST
    self.last_cmd_time = time.monotonic()

    print(f"[Drone] {self.drone.id} deactivated.")



# ============================================================
# PUB/SUB
# ============================================================
def initialize_handles():
    self.cmd_vel_sub = None
    self.reset_pose_sub = None
    self.activate_sub = None
    self.deactivate_sub = None
    self.status_pub = None

def receive_messages():
    self.cmd_vel_sub.receive()
    self.reset_pose_sub.receive()
    self.activate_sub.receive()
    self.deactivate_sub.receive()

def initialize_pubsub():
    # Reset pose
    self.reset_pose_sub = Subscriber(
        topic=f"{self.drone.id}.reset_pose",
        message_type=Pose,
        callback=on_reset_pose
    )

    # Velocity commands
    self.cmd_vel_sub = Subscriber(
        topic=f"{self.drone.id}.cmd_vel",
        message_type=Twist,
        callback=on_cmd_vel
    )

    # Activation commands
    self.activate_sub = Subscriber(
        topic=f"{self.drone.id}.activate",
        message_type=RobotActivationMessage,
        callback=on_activate
    )

    self.deactivate_sub = Subscriber(
        topic=f"{self.drone.id}.deactivate",
        message_type=RobotDeactivationMessage,
        callback=on_deactivate
    )

    # Status publisher
    self.status_pub = Publisher(
        topic=f"{self.drone.id}.status"
    )


# ============================================================
# INITIALIZATION
# ============================================================

def sysCall_init():

    global sim
    sim = require("sim")

    initialize_handles()

    # Object references
    self.drone_handle = sim.getObject("..")
    self.target_handle = sim.getObject("../target")
    self.base_handle = sim.getObject("../base")

    # Detach target while preserving world pose
    sim.setObjectParent(
        self.target_handle,
        -1,
        True
    )

    # Generate robot ID
    robot_id = get_next_drone_id(sim)

    print(f"[Drone ID] Generated: {robot_id}")

    # Initial pose
    position = sim.getObjectPosition(
        self.drone_handle,
        -1
    )

    orientation = sim.getObjectOrientation(
        self.drone_handle,
        -1
    )

    init_pose = Pose.from_coordinates(
        x=position[0],
        y=position[1],
        z=position[2],
        yaw=orientation[2]
    )

    # Initialize drone
    self.drone = Drone(
        id=str(robot_id),
        init_pose=init_pose,
        init_soc=100.0,
        config=Drone.DEFAULT_CONFIG
    )

    self.dt = sim.getSimulationTimeStep()

    # Initial state: stored
    self.active = False

    # Initial command
    self.cmd_vel = ZERO_TWIST
    self.last_cmd_time = time.monotonic()

    # Initialize communication
    initialize_pubsub()


# ============================================================
# ACTUATION
# ============================================================

def sysCall_actuation():

    # Receive pending messages
    receive_messages()

    # Do not update drone while stored
    if not self.active:
        return

    # Command timeout
    if time.monotonic() - self.last_cmd_time > COMMAND_TIMEOUT:
        self.cmd_vel = ZERO_TWIST

    # Update drone
    self.drone.move(
        self.cmd_vel,
        self.dt
    )

    set_target_pose(
        self.drone.pose,
        self.target_handle
    )

    # Publish status
    self.status_pub.publish(
        RobotStatusMessage.from_robot(self.drone)
    )


# ============================================================
# SENSING
# ============================================================

def sysCall_sensing():
    pass


# ============================================================
# CLEANUP
# ============================================================

def sysCall_cleanup():

    subscribers = [
        self.cmd_vel_sub,
        self.reset_pose_sub,
        self.activate_sub,
        self.deactivate_sub
    ]

    for subscriber in subscribers:
        if subscriber is not None:
            subscriber.close()

    if self.status_pub is not None:
        self.status_pub.close()