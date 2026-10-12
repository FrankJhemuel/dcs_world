import numpy as np
from abc import ABC, abstractmethod

from dcs_world.geometry.pose import Pose
from .robot_utils import RobotStatus, RobotConfig


class Robot(ABC):
    """Represent an abstract robot in the simulated world.

    Attributes:
        charge (float): Current battery charge as a percentage (0–100).
        status (RobotStatus): Current operational status of the robot.
        config (RobotConfig): Configuration parameters of the robot.
    """

    def __init__(
        self,
        init_x: float = 0.0,
        init_y: float = 0.0,
        init_yaw: float = 0.0,
        init_charge: float = 100.0,
        config: RobotConfig | None = None,
    ) -> None:
        """Initialize the robot's state and configuration.

        Args:
            init_x (float, optional): Initial x-coordinate. Defaults to 0.0.
            init_y (float, optional): Initial y-coordinate. Defaults to 0.0.
            init_yaw (float, optional): Initial orientation in radians.
                Defaults to 0.0.
            init_charge (float, optional): Initial battery charge as a
                percentage between 0 and 100. Defaults to 100.0.
            config (RobotConfig | None, optional): Robot configuration.
                Must be a RobotConfig instance. Defaults to None.

        Raises:
            TypeError: If a numeric parameter is not an integer or float,
                or if a numeric parameter is a boolean.
            TypeError: If config is not a RobotConfig instance.
            ValueError: If init_charge is outside the range [0, 100].
            ValueError: If config is None.

        Notes:
            The initial position and orientation are converted to floats.
            The robot's initial status is set to RobotStatus.IDLE.
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
        self.__pose = Pose(
            x=float(init_x),
            y=float(init_y),
            yaw=float(init_yaw),
        )
        self.charge = float(init_charge)
        self.status = RobotStatus.IDLE

        # Store configuration
        self.config = config

    @property
    def pose(self) -> Pose:
        """Return a copy of the robot's current pose.

        Returns:
            Pose: A new Pose instance containing the current position
                and orientation of the robot.

        Notes:
            Returning a copy prevents external modifications from directly
            changing the robot's internal pose.
        """
        return Pose(
            x=self.__pose.x,
            y=self.__pose.y,
            yaw=self.__pose.yaw,
        )

    @property
    def telemetry(self) -> dict:
        """Return the robot's current telemetry.

        Returns:
            dict: A dictionary containing the robot's current pose,
                battery charge, and operational status. The dictionary
                has the following keys:
                - "pose": Current pose as a Pose instance.
                - "charge": Current battery charge as a percentage.
                - "status": Current operational status as a RobotStatus.
        """
        return {
            "pose": self.pose,
            "charge": self.charge,
            "status": self.status,
        }

    @abstractmethod
    def move(self, cmd_vel: np.ndarray) -> None:
        """Update the robot's motion according to a velocity command.

        Args:
            cmd_vel (np.ndarray): Array containing the commanded velocity
                components. Its shape and interpretation depend on the
                concrete robot implementation.

        Raises:
            NotImplementedError: If the method is not overridden by a
                concrete subclass.

        Notes:
            Subclasses must implement this method to define the robot's
            movement behavior.
        """
        raise NotImplementedError("Movement is not implemented yet.")