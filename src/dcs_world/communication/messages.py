from dataclasses import dataclass
from typing import Literal
import time

from dcs_world.geometry.pose import Pose
from dcs_world.geometry.position import Position
from dcs_world.geometry.twist import Twist
from dcs_world.robot.utils.robot_status import RobotStatus

@dataclass
class TwistStamped:
    """Represent a velocity command with a timestamp."""

    timestamp: float
    twist: Twist
    
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
    def from_robot(robot: "Robot") -> "RobotStatusMessage": #type: ignore
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
    
@dataclass
class CivilianMessage:
    """Represent the observations collected by a civilian."""
    
    timestamp: float
    building_position: Position
    n_civilians: int
    
@dataclass
class ObstacleMessage:
    """Represent the observations collected by a robot regarding obstacles."""
    
    timestamp: float
    position: Position
    
@dataclass
class POIMessage:
    """Represent the observations collected by a drone."""
    
    timestamp: float
    building_position: Position