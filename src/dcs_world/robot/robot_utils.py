import json
from enum import Enum, auto
from dataclasses import dataclass


@dataclass
class RobotConfig:
    """Store the configuration parameters of a robot.

    Attributes:
        id (str): Unique identifier of the robot.
        max_speed (float): Maximum allowed speed of the robot.
        max_accel (float): Maximum allowed acceleration of the robot.
    """

    id: str
    max_speed: float
    max_accel: float

    @classmethod
    def from_json(cls, json_str: str) -> "RobotConfig":
        """Create a RobotConfig instance from a JSON string.

        Args:
            json_str (str): JSON string containing the robot configuration.
                Expected keys are 'id', 'max_speed', and 'max_accel'.

        Raises:
            ValueError: If the JSON is invalid, a required key is missing,
                or the decoded JSON has an incompatible structure.

        Returns:
            RobotConfig: A new instance initialized with the decoded
                configuration parameters.
        """
        try:
            data = json.loads(json_str)
            return cls(
                id=data["id"],
                max_speed=data["max_speed"],
                max_accel=data["max_accel"],
            )
        except (KeyError, TypeError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid JSON for RobotConfig: {e}") from e


class RobotStatus(Enum):
    """Represent the possible operational states of a robot."""

    IDLE = auto()
    CHARGING = auto()
    EXECUTING = auto()
    MOVING = auto()
    ERROR = auto()

    # Drone-specific states
    FLYING = auto()
    LANDING = auto()