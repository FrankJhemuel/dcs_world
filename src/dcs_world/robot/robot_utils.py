import json
from enum import Enum, auto
from dataclasses import dataclass

@dataclass
class RobotConfig:
    id: str
    max_speed: float
    max_accel: float
    
    @classmethod
    def from_json(cls, json_str: str) -> 'RobotConfig':
        """
        @brief Create a RobotConfig instance from a JSON string.

        @param json_str JSON string representing the robot configuration.
        @return RobotConfig instance.
        """
        try:
            data = json.loads(json_str)
            return cls(
                id=data['id'],
                max_speed=data['max_speed'],
                max_accel=data['max_accel']
            )
        except (KeyError, TypeError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid JSON for RobotConfig: {e}")
    

class RobotStatus(Enum):
    IDLE = auto()
    CHARGING = auto()
    EXECUTING = auto()
    MOVING = auto()
    ERROR = auto()