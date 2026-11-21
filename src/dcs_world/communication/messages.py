from dataclasses import dataclass
from typing import Literal
import time

from dcs_world.geometry.pose import Pose
from dcs_world.geometry.position import Position
from dcs_world.geometry.twist import Twist
from dcs_world.robot.utils.robot_status import RobotStatus


# ============================================================
# BASIC MESSAGES
# ============================================================

@dataclass
class TwistStamped:
    """Represent a velocity command with a timestamp."""

    timestamp: float
    twist: Twist


# ============================================================
# ROBOT MANAGEMENT MESSAGES
# ============================================================

@dataclass
class RobotActivationMessage:
    robot_id: str


@dataclass
class RobotDeactivationMessage:
    robot_id: str


@dataclass
class RobotDeploymentMessage:
    robot_id: str


@dataclass
class RobotStorageMessage:
    robot_id: str


@dataclass
class RobotStatusMessage:
    """Represent the status of a robot."""

    timestamp: float
    id: str
    robot_type: Literal["Drone", "GroundRobot"]
    pose: Pose
    velocity: Twist
    soc: float
    status: RobotStatus

    @staticmethod
    def from_robot(robot: "Robot") -> "RobotStatusMessage":  # type: ignore
        """Create a RobotStatusMessage from a robot instance."""

        return RobotStatusMessage(
            timestamp=time.time(),
            id=robot.id,
            robot_type=robot.ROBOT_TYPE,
            pose=robot.pose,
            velocity=robot.velocity,
            soc=robot.soc,
            status=robot.status
        )


# ============================================================
# OBSERVATION MESSAGES
# ============================================================

@dataclass
class CivilianMessage:
    """Represent observations collected by a robot regarding civilians."""

    timestamp: float
    robot_id: str
    building_position: Position
    n_civilians: int


@dataclass
class ObstacleMessage:
    """Represent observations collected by a robot regarding obstacles."""

    timestamp: float
    robot_id: str
    position: Position


@dataclass
class POIMessage:
    """Represent observations collected by a drone regarding points of interest."""

    timestamp: float
    robot_id: str
    building_position: Position
