import os

from dcs_world.communication import Publisher, Subscriber
from dcs_world.communication.messages import (
    RobotDeploymentMessage,
    RobotStorageMessage,
    RobotActivationMessage,
    RobotDeactivationMessage
)
from dcs_world.geometry import Pose

from dcs_world.coppelia.utils import DRONE_ID_SIGNAL


# ============================================================
# CONFIGURATION
# ============================================================

NUM_DRONES = 5
DRONE_NAME_PREFIX = "drone"

DRONE_MODEL_FILENAME = "drone.ttm"

DEPLOY_TOPIC = "base.deploy"
STORE_TOPIC = "base.store"


# ============================================================
# INITIALIZATION
# ============================================================

def sysCall_init():

    global sim
    sim = require("sim")

    # --------------------------------------------------------
    # MODEL PROPERTIES
    # --------------------------------------------------------

    global INACTIVE_PROPERTIES

    INACTIVE_PROPERTIES = (
        sim.modelproperty_not_visible
        | sim.modelproperty_not_dynamic
        | sim.modelproperty_not_respondable
    )

    # --------------------------------------------------------
    # SIMULATION OBJECTS
    # --------------------------------------------------------

    self.base_handle = sim.getObject("..")

    self.deployment_point = sim.getObject(
        "../DeploymentPoint"
    )

    # --------------------------------------------------------
    # ROBOT REGISTRY
    # --------------------------------------------------------

    self.drones = {}
    self.model_properties = {}

    # --------------------------------------------------------
    # COMMUNICATION REGISTRY
    # --------------------------------------------------------

    self.pose_publishers = {}
    self.activation_publishers = {}
    self.deactivation_publishers = {}

    # --------------------------------------------------------
    # COMMUNICATION
    # --------------------------------------------------------

    self.deploy_subscriber = Subscriber(
        topic=DEPLOY_TOPIC,
        message_type=RobotDeploymentMessage,
        callback=on_deploy
    )

    self.store_subscriber = Subscriber(
        topic=STORE_TOPIC,
        message_type=RobotStorageMessage,
        callback=on_store
    )

    # --------------------------------------------------------
    # INITIALIZE DRONE INVENTORY
    # --------------------------------------------------------

    initialize_drone_inventory()

    print(
        f"[Base] Initialized with {len(self.drones)} drones."
    )


# ============================================================
# SIMULATION CALLBACKS
# ============================================================

def sysCall_actuation():

    self.deploy_subscriber.receive()
    self.store_subscriber.receive()


def sysCall_cleanup():

    # --------------------------------------------------------
    # SUBSCRIBERS
    # --------------------------------------------------------

    self.deploy_subscriber.close()
    self.store_subscriber.close()

    # --------------------------------------------------------
    # PER-DRONE PUBLISHERS
    # --------------------------------------------------------

    for publisher in self.pose_publishers.values():
        publisher.close()

    for publisher in self.activation_publishers.values():
        publisher.close()

    for publisher in self.deactivation_publishers.values():
        publisher.close()

    print("[Base] Stopped.")


# ============================================================
# DRONE INVENTORY
# ============================================================

def initialize_drone_inventory():

    # --------------------------------------------------------
    # RESOLVE MODEL PATH
    # --------------------------------------------------------

    scene_path = sim.getStringParam(
        sim.stringparam_scene_path
    )

    scene_dir = os.path.dirname(scene_path)

    model_dir = os.path.join(
        scene_dir,
        "model"
    )

    drone_model_path = os.path.join(
        model_dir,
        DRONE_MODEL_FILENAME
    )

    if not os.path.isfile(drone_model_path):
        raise FileNotFoundError(
            f"Drone model not found: {drone_model_path}"
        )

    # --------------------------------------------------------
    # DETERMINE INITIAL ID COUNTER
    # --------------------------------------------------------

    counter = sim.getInt32Signal(DRONE_ID_SIGNAL)

    if counter is None:
        counter = 0

    # --------------------------------------------------------
    # DEPLOYMENT POSITION
    # --------------------------------------------------------

    position = sim.getObjectPosition(
        self.deployment_point,
        -1
    )

    orientation = sim.getObjectOrientation(
        self.deployment_point,
        -1
    )

    # --------------------------------------------------------
    # LOAD DRONE MODELS
    # --------------------------------------------------------

    for i in range(NUM_DRONES):

        robot_id = (
            f"{DRONE_NAME_PREFIX}_{counter + i + 1}"
        )

        print(f"[Base] Loading {robot_id}...")

        # Load model
        drone_handle = sim.loadModel(
            drone_model_path
        )

        # Assign model alias
        sim.setObjectAlias(
            drone_handle,
            robot_id
        )

        # ----------------------------------------------------
        # INITIAL POSITION
        # ----------------------------------------------------

        sim.setObjectPosition(
            drone_handle,
            -1,
            position
        )

        sim.setObjectOrientation(
            drone_handle,
            -1,
            orientation
        )

        # ----------------------------------------------------
        # SAVE ORIGINAL MODEL PROPERTIES
        # ----------------------------------------------------

        self.model_properties[robot_id] = (
            sim.getModelProperty(drone_handle)
        )

        # ----------------------------------------------------
        # DEACTIVATE DRONE
        # ----------------------------------------------------

        deactivate_drone(drone_handle)

        # ----------------------------------------------------
        # REGISTER MODEL HANDLE
        # ----------------------------------------------------

        self.drones[robot_id] = drone_handle

        # ----------------------------------------------------
        # COMMUNICATION PUBLISHERS
        # ----------------------------------------------------

        self.pose_publishers[robot_id] = Publisher(
            topic=f"{robot_id}.reset_pose"
        )

        self.activation_publishers[robot_id] = Publisher(
            topic=f"{robot_id}.activate"
        )

        self.deactivation_publishers[robot_id] = Publisher(
            topic=f"{robot_id}.deactivate"
        )

        print(f"[Base] Loaded {robot_id}.")

    print(
        f"[Base] Successfully loaded {NUM_DRONES} drones."
    )


# ============================================================
# DRONE DEPLOYMENT
# ============================================================

def on_deploy(message: RobotDeploymentMessage):

    robot_id = message.robot_id

    try:

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        drone_handle = self.drones.get(robot_id)

        if drone_handle is None:
            raise ValueError(
                f"Unknown drone: {robot_id}"
            )

        current_properties = sim.getModelProperty(
            drone_handle
        )

        if not (
            current_properties
            & sim.modelproperty_not_visible
        ):
            raise ValueError(
                f"{robot_id} is already deployed."
            )

        # ----------------------------------------------------
        # DEPLOYMENT POSE
        # ----------------------------------------------------

        position = sim.getObjectPosition(
            self.deployment_point,
            -1
        )

        orientation = sim.getObjectOrientation(
            self.deployment_point,
            -1
        )

        pose = Pose.from_coordinates(
            x=position[0],
            y=position[1],
            z=position[2],
            yaw=orientation[2]
        )

        # ----------------------------------------------------
        # POSITION MODEL
        # ----------------------------------------------------

        sim.setObjectPosition(
            drone_handle,
            -1,
            position
        )

        sim.setObjectOrientation(
            drone_handle,
            -1,
            orientation
        )

        # ----------------------------------------------------
        # SYNCHRONIZE INTERNAL DRONE POSE
        # ----------------------------------------------------

        self.pose_publishers[robot_id].publish(pose)

        # ----------------------------------------------------
        # ACTIVATE DRONE
        # ----------------------------------------------------

        activate_drone(
            drone_handle,
            robot_id
        )

        self.activation_publishers[robot_id].publish(
            RobotActivationMessage(robot_id=robot_id)
        )

        print(f"[Base] Deployed {robot_id}.")

    except Exception as error:

        print(
            f"[Base] Deployment failed for {robot_id}: {error}"
        )


# ============================================================
# DRONE STORAGE
# ============================================================

def on_store(message: RobotStorageMessage):

    robot_id = message.robot_id

    try:

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        drone_handle = self.drones.get(robot_id)

        if drone_handle is None:
            raise ValueError(
                f"Unknown drone: {robot_id}"
            )

        current_properties = sim.getModelProperty(
            drone_handle
        )

        if (
            current_properties
            & sim.modelproperty_not_visible
        ):
            raise ValueError(
                f"{robot_id} is already stored."
            )

        # ----------------------------------------------------
        # DEACTIVATE DRONE
        # ----------------------------------------------------

        self.deactivation_publishers[robot_id].publish(
            RobotDeactivationMessage(robot_id=robot_id)
        )

        deactivate_drone(drone_handle)

        print(f"[Base] Stored {robot_id}.")

    except Exception as error:

        print(
            f"[Base] Storage failed for {robot_id}: {error}"
        )


# ============================================================
# MODEL ACTIVATION
# ============================================================

def activate_drone(
    drone_handle: int,
    robot_id: str
):

    original_properties = self.model_properties[robot_id]

    sim.setModelProperty(
        drone_handle,
        original_properties
    )


def deactivate_drone(drone_handle: int):

    properties = sim.getModelProperty(
        drone_handle
    )

    sim.setModelProperty(
        drone_handle,
        properties | INACTIVE_PROPERTIES
    )