from dataclasses import dataclass
from typing import Literal

from dcs_world.geometry.pose import Pose
from dcs_world.geometry.twist import Twist
from dcs_world.robot.utils.robot_status import RobotStatus

@dataclass
class RobotModel:
    """Robot model representing the state of a robot."""
    
    id: str
    robot_type: Literal["Drone", "GroundRobot"]
    pose: Pose
    velocity: Twist
    soc: float
    status: RobotStatus