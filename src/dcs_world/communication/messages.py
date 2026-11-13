from dataclasses import dataclass
from typing import Literal
from dcs_world.geometry.pose import Pose
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