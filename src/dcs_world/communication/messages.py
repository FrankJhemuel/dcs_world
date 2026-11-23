from dataclasses import dataclass
from enum import Enum, auto
from typing import Literal
import time

from dcs_world.geometry.pose import Pose
from dcs_world.geometry.position import Position
from dcs_world.geometry.twist import Twist
from dcs_world.robot.utils.deployment_state import DeploymentState
from dcs_world.robot.utils.robot_status import RobotStatus
from dcs_world.robot.utils.task_status import TaskStatus


# ============================================================
# BASIC MESSAGES
# ============================================================

@dataclass
class TwistStamped:
    """Represent a velocity command with a timestamp."""

    timestamp: float
    twist: Twist

# ============================================================
# TASK MESSAGES
# ============================================================


@dataclass
class ExplorationTaskMessage:
    task_id: str
    targets: list[Pose]


class ExplorationResponseStatus(Enum):
    ACCEPTED = auto()
    REJECTED = auto()
    COMPLETED = auto()
    FAILED = auto()


@dataclass
class ExplorationResponseMessage:
    task_id: str
    id: str
    status: ExplorationResponseStatus
    reason: str = ""

# ============================================================
# ROBOT MANAGEMENT MESSAGES
# ============================================================


@dataclass
class RobotActivationMessage:
    id: str


@dataclass
class RobotDeactivationMessage:
    id: str


@dataclass
class RobotDeploymentMessage:
    id: str


@dataclass
class RobotStorageMessage:
    id: str


class RobotManagementStatus(Enum):
    SUCCEEDED = auto()
    FAILED = auto()


@dataclass
class RobotManagementResponseMessage:
    id: str
    status: RobotManagementStatus
    reason: str = ""


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
    deployment_state: DeploymentState
    task_status: TaskStatus

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
            status=robot.status,
            deployment_state=robot.deployment_state,
            task_status=robot.task_status
        )


# ============================================================
# OBSERVATION MESSAGES
# ============================================================

@dataclass
class CivilianMessage:
    """Represent observations collected by a robot regarding civilians."""

    timestamp: float
    id: str
    building_position: Position
    n_civilians: int


@dataclass
class ObstacleMessage:
    """Represent observations collected by a robot regarding obstacles."""

    timestamp: float
    id: str
    position: Position


@dataclass
class POIMessage:
    """Represent observations collected by a drone regarding points of interest."""

    timestamp: float
    id: str
    building_position: Position
