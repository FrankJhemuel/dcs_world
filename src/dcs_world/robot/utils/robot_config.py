from dataclasses import dataclass
import json

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
    charge_use_rate_per_meter: float = 0.1  # Default charge use rate per meter traveled

    @classmethod
    def from_json(cls, json_str: str) -> "RobotConfig":
        """Create a RobotConfig instance from a JSON string.

        Args:
            json_str (str): JSON string containing the robot configuration.
                Expected keys are 'id', 'max_speed', 'max_accel', and 'charge_use_rate_per_meter'.

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
                charge_use_rate_per_meter=data["charge_use_rate_per_meter"],
            )
        except (KeyError, TypeError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid JSON for RobotConfig: {e}") from e
