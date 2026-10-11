import numpy as np

from dcs_world.geometry.pose import Pose
from .robot_utils import RobotStatus, RobotConfig

class Robot:
    """Represent a robot in the simulated world."""

    def __init__(
        self,
        init_x: float = 0.0,
        init_y: float = 0.0,
        init_yaw: float = 0.0,
        init_charge: float = 100.0,
        config: RobotConfig | None = None,
    ) -> None:
        """
        @brief Initialize the robot with an initial pose and charge level.

        @param init_x Initial x-coordinate in meters.
        @param init_y Initial y-coordinate in meters.
        @param init_yaw Initial heading in radians.
        @param init_charge Initial battery charge percentage (0–100).
        @param config Configuration for the robot.
        """

        # Validate numeric inputs
        numeric_params = {
            "init_x": init_x,
            "init_y": init_y,
            "init_yaw": init_yaw,
            "init_charge": init_charge,
        }

        for name, value in numeric_params.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a numeric value.")

        # Validate ranges
        if not 0.0 <= init_charge <= 100.0:
            raise ValueError("Initial charge must be between 0 and 100.")

        # Validate configuration
        if config is None:
            raise ValueError("Robot configuration must be provided.")

        if not isinstance(config, RobotConfig):
            raise TypeError("config must be an instance of RobotConfig.")

        # Initialize state
        self.pose = Pose(
            x=float(init_x),
            y=float(init_y),
            yaw=float(init_yaw),
        )
        self.charge = float(init_charge)
        self.status = RobotStatus.IDLE

        # Store configuration
        self.config = config

    @property
    def telemetry(self) -> dict:
        """
        @brief Get the robot's current telemetry.

        @return A dictionary containing the current pose, charge, and status.
        """
        return {
            "pose": self.pose,
            "charge": self.charge,
            "status": self.status,
        }

    def move_towards(self, new_x: float, new_y: float) -> None:
        """
        @brief Move the robot towards a target position.

        @param new_x Target x-coordinate in meters.
        @param new_y Target y-coordinate in meters.
        """
        raise NotImplementedError("Movement is not implemented yet.")