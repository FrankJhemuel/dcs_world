from dataclasses import dataclass, fields, is_dataclass
from typing import Literal

from zmq import Enum

from dcs_world.geometry.pose import Pose
from dcs_world.geometry.twist import Twist
from dcs_world.robot.utils.robot_status import RobotStatus
from dcs_world.robot.utils.deployment_state import DeploymentState
from dcs_world.robot.utils.task_status import TaskStatus

def _to_dict(value):
    """Recursively convert objects into JSON-compatible values."""

    if isinstance(value, Enum):
        return value.name

    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _to_dict(getattr(value, field.name))
            for field in fields(value)
        }

    if isinstance(value, list):
        return [_to_dict(item) for item in value]

    if isinstance(value, dict):
        return {
            key: _to_dict(item)
            for key, item in value.items()
        }

    return value

@dataclass
class RobotModel:
    """Robot model representing the state of a robot."""
    
    timestamp: float
    id: str
    robot_type: Literal["Drone", "GroundRobot"]
    pose: Pose
    velocity: Twist
    soc: float
    status: RobotStatus
    task_status: TaskStatus
    deployment_state: DeploymentState
    
    @classmethod
    def from_status_message(cls, message: 'RobotStatusMessage') -> 'RobotModel': #type: ignore
        """Create a RobotModel from a RobotStatusMessage."""
        if message is None:
            raise ValueError("message cannot be None.")
        
        model_fields = {
            field.name
            for field in fields(cls)
        }

        values = {
            name: getattr(message, name)
            for name in model_fields
        }

        return cls(**values)
    
    def to_dict(self) -> dict:
        """Convert the robot model into a dictionary."""

        return _to_dict(self)