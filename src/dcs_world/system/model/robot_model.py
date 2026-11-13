from dataclasses import asdict, dataclass
from typing import Literal
import json

from dcs_world.geometry.pose import Pose
from dcs_world.geometry.twist import Twist
from dcs_world.robot.utils.robot_status import RobotStatus

@dataclass
class RobotModel:
    """Data Transfer Object for Robot information."""
    
    id: str
    robot_type: Literal["Drone", "GroundRobot"]
    pose: Pose
    velocity: Twist
    soc: float
    status: RobotStatus
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data["status"] = self.status.name
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    