import numpy as np

from dcs_world.geometry.pose import Pose
from .robot_utils import RobotStatus, RobotConfig


class Robot():
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
        
        # Validate finite numeric inputs
        if not all(np.isfinite(value) for value in numeric_params.values()):
            raise ValueError("Numeric parameters must be finite.")

        # Validate ranges
        if not 0.0 <= init_charge <= 100.0:
            raise ValueError("Initial charge must be between 0 and 100.")

        # Validate configuration
        if config is None:
            raise ValueError("Robot configuration must be provided.")

        if not isinstance(config, RobotConfig):
            raise TypeError("config must be an instance of RobotConfig.")

        # Initialize state
        self._pose = Pose(
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
            x=self._pose.x,
            y=self._pose.y,
            yaw=self._pose.yaw,
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

    def move(self, cmd_vel: np.ndarray, dt: float) -> None:
        """Update the robot's pose according to a velocity command.

        Args:
            cmd_vel (np.ndarray): One-dimensional NumPy array containing
                the velocity components [vx, vy, omega], where vx and vy
                are translational velocities and omega is the angular
                velocity.
            dt (float): Time step in seconds over which the velocity
                command is applied.

        Raises:
            TypeError: If cmd_vel is not a NumPy array or dt is not numeric.
            ValueError: If cmd_vel does not have shape (3,) or dt is not
                finite and positive.

        Notes:
            This method provides a default implementation that updates the
            robot's pose by integrating the commanded velocities over dt.
            Subclasses may override this method to implement robot-specific
            motion models.
        """
        # Validate cmd_vel and dt
        if not isinstance(cmd_vel, np.ndarray):
            raise TypeError("cmd_vel must be a NumPy ndarray.")

        if cmd_vel.shape != (3,):
            raise ValueError("cmd_vel must be a 1D array with exactly 3 elements.")

        if not np.issubdtype(cmd_vel.dtype, np.number):
            raise TypeError("cmd_vel must contain numeric values.")

        if not np.all(np.isfinite(cmd_vel)):
            raise ValueError("cmd_vel must contain only finite values.")

        if isinstance(dt, bool) or not isinstance(dt, (int, float)):
            raise TypeError("dt must be a numeric value.")

        if not np.isfinite(dt) or dt <= 0:
            raise ValueError("dt must be finite and positive.")

        # Update the robot's pose based on the commanded velocity and time step
        delta_pose = cmd_vel * dt
        self._pose.as_np_array = self._pose.as_np_array + delta_pose