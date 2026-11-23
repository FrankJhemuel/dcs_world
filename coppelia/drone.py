from dcs_world.robot.drone import Drone
from dcs_world.communication import Subscriber, Publisher
from dcs_world.geometry import Pose
from dcs_world.communication.messages import (
    RobotStatusMessage,
    RobotActivationMessage,
    RobotDeactivationMessage,
    ExplorationTaskMessage,
)
from dcs_world.coppelia.utils import get_next_drone_id


# ============================================================
# CALLBACKS
# ============================================================

def set_target_pose(pose, target_handle):
    """Update the target visualization in CoppeliaSim."""

    sim.setObjectPosition(
        target_handle,
        -1,
        [pose.x, pose.y, pose.z],
    )

    sim.setObjectOrientation(
        target_handle,
        -1,
        [0.0, 0.0, pose.yaw],
    )


# ------------------------------------------------------------
# Robot callbacks
# ------------------------------------------------------------

def on_reset_pose(msg: Pose):
    """Reset the drone pose."""

    self.drone.reset_pose(msg)

    set_target_pose(
        self.drone.pose,
        self.target_handle,
    )


def on_activate(msg: RobotActivationMessage):
    """Activate the drone."""

    self.active = True

    print(f"[Drone] {self.drone.id} activated.")


def on_deactivate(msg: RobotDeactivationMessage):
    """Deactivate the drone."""

    self.active = False

    print(f"[Drone] {self.drone.id} deactivated.")


# ------------------------------------------------------------
# Exploration callbacks
# ------------------------------------------------------------

def on_exploration_request(msg: ExplorationTaskMessage):
    """Process an exploration task request."""

    response = self.drone.assign_exploration(msg)

    self.exploration_response_pub.publish(response)

    print(
        f"[Drone] Exploration task {msg.task_id}: "
        f"{response.status.name}"
    )


# ============================================================
# COMMUNICATION
# ============================================================

def initialize_handles():
    """Initialize communication endpoint collections."""

    self.subscribers = []
    self.publishers = []


def initialize_pubsub():

    # --------------------------------------------------------
    # Subscribers
    # --------------------------------------------------------

    # Reset pose
    self.reset_pose_sub = Subscriber(
        topic=f"{self.drone.id}.reset_pose",
        message_type=Pose,
        callback=on_reset_pose,
    )

    # Activation commands
    self.activate_sub = Subscriber(
        topic=f"{self.drone.id}.activate",
        message_type=RobotActivationMessage,
        callback=on_activate,
    )

    # Deactivation commands
    self.deactivate_sub = Subscriber(
        topic=f"{self.drone.id}.deactivate",
        message_type=RobotDeactivationMessage,
        callback=on_deactivate,
    )

    # Exploration task requests
    self.exploration_request_sub = Subscriber(
        topic=f"{self.drone.id}.explore.request",
        message_type=ExplorationTaskMessage,
        callback=on_exploration_request,
    )

    # --------------------------------------------------------
    # Publishers
    # --------------------------------------------------------

    # Robot status
    self.status_pub = Publisher(
        topic=f"{self.drone.id}.status",
        handshake=True,
    )

    # Exploration task responses
    self.exploration_response_pub = Publisher(
        topic=f"{self.drone.id}.explore.response",
        handshake=True,
    )

    # --------------------------------------------------------
    # Register endpoints
    # --------------------------------------------------------

    self.subscribers = [
        self.reset_pose_sub,
        self.activate_sub,
        self.deactivate_sub,
        self.exploration_request_sub,
    ]

    self.publishers = [
        self.status_pub,
        self.exploration_response_pub,
    ]


def receive_messages():
    """Process pending messages from all subscribers."""

    for subscriber in self.subscribers:
        subscriber.receive()


def publish_pending_task_response():
    """Publish a pending exploration lifecycle response."""

    response = self.drone.consume_task_response()

    if response is not None:
        self.exploration_response_pub.publish(response)

        print(
            f"[Drone] Exploration task {response.task_id}: "
            f"{response.status.name}"
        )


def publish_status():
    """Publish the current robot status."""

    self.status_pub.publish(
        RobotStatusMessage.from_robot(self.drone)
    )


def cleanup_pubsub():
    """Close all communication endpoints."""

    for endpoint in self.subscribers + self.publishers:
        endpoint.close()

    self.subscribers.clear()
    self.publishers.clear()


# ============================================================
# INITIALIZATION
# ============================================================

def sysCall_init():

    global sim
    sim = require("sim")

    initialize_handles()

    # --------------------------------------------------------
    # Object references
    # --------------------------------------------------------

    self.drone_handle = sim.getObject("..")
    self.target_handle = sim.getObject("../target")
    self.base_handle = sim.getObject("../base")

    # Detach target while preserving world pose
    sim.setObjectParent(
        self.target_handle,
        -1,
        True,
    )

    # --------------------------------------------------------
    # Robot identification
    # --------------------------------------------------------

    robot_id = get_next_drone_id(sim)

    print(f"[Drone ID] Generated: {robot_id}")

    # --------------------------------------------------------
    # Initial pose
    # --------------------------------------------------------

    position = sim.getObjectPosition(
        self.drone_handle,
        -1,
    )

    orientation = sim.getObjectOrientation(
        self.drone_handle,
        -1,
    )

    init_pose = Pose.from_coordinates(
        x=position[0],
        y=position[1],
        z=position[2],
        yaw=orientation[2],
    )

    # --------------------------------------------------------
    # Drone initialization
    # --------------------------------------------------------

    self.drone = Drone(
        id=str(robot_id),
        init_pose=init_pose,
        init_soc=100.0,
        config=Drone.DEFAULT_CONFIG,
    )

    self.dt = sim.getSimulationTimeStep()

    # Initial state: stored
    self.active = False

    # --------------------------------------------------------
    # Communication initialization
    # --------------------------------------------------------

    initialize_pubsub()

    # Initial status publication
    publish_status()

    print(
        f"Publishing initial status for drone {self.drone.id} "
        f"in topic '{self.status_pub.topic}'."
    )


# ============================================================
# ACTUATION
# ============================================================

def sysCall_actuation():

    # --------------------------------------------------------
    # Receive pending messages
    # --------------------------------------------------------

    receive_messages()

    # Do not update drone while stored
    if not self.active:
        return

    # --------------------------------------------------------
    # Execute autonomous behavior
    # --------------------------------------------------------

    self.drone.run(self.dt)

    # --------------------------------------------------------
    # Publish task lifecycle events
    # --------------------------------------------------------

    publish_pending_task_response()

    # --------------------------------------------------------
    # Update target visualization
    # --------------------------------------------------------

    set_target_pose(
        self.drone.pose,
        self.target_handle,
    )

    # --------------------------------------------------------
    # Publish robot telemetry
    # --------------------------------------------------------

    publish_status()


# ============================================================
# SENSING
# ============================================================

def sysCall_sensing():
    pass


# ============================================================
# CLEANUP
# ============================================================

def sysCall_cleanup():
    cleanup_pubsub()