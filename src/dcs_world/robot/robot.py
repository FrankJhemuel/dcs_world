import numpy as np
import uuid

from dcs_world.geometry.pose import Pose
from .utils import RobotStatus, RobotConfig


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
        
        self.id = str(uuid.uuid4())  # Unique identifier for the robot
        
        # Initialize state
        self._pose = Pose(
            x=float(init_x),
            y=float(init_y),
            yaw=float(init_yaw),
        )
        self.charge = float(init_charge)
        self.status = RobotStatus.IDLE

        self._velocity = np.zeros(3)  # [vx, vy, omega] in m/s and rad/s
        
        # Store configuration
        self.config = config
        
        
        self.observations: list[dict] = []
        
    def add_observation(self, observation: dict) -> None:
        """Add an observation to the robot's observations list."""
        self.observations.append(observation)

    def clear_observations(self) -> None:
        """Clear the robot's observations list."""
        self.observations.clear()
        
    @property
    def pose(self) -> np.ndarray:
        """Return a copy of the robot's current pose.

        Returns:
            np.ndarray: A one-dimensional NumPy array containing the
                current position and orientation of the robot.

        Notes:
            Returning a copy prevents external modifications from directly
            changing the robot's internal pose.
        """
        return np.array([self._pose.x, self._pose.y, self._pose.yaw])

    @property
    def velocity(self) -> np.ndarray:
        """Return a copy of the robot's current velocity.

        Returns:
            np.ndarray: A one-dimensional NumPy array containing the
                current velocity components [vx, vy, omega], where vx
                and vy are translational velocities in m/s and omega is
                the angular velocity in rad/s.

        Notes:
            Returning a copy prevents external modifications from directly
            changing the robot's internal velocity.
        """
        return self._velocity.copy()

    @velocity.setter
    def velocity(self, value: np.ndarray) -> None:
        """Set the robot's current velocity.

        Args:
            value (np.ndarray): A one-dimensional NumPy array containing
                the new velocity components [vx, vy, omega], where vx and
                vy are translational velocities in m/s and omega is the
                angular velocity in rad/s.

        Raises:
            TypeError: If value is not a NumPy array.
            ValueError: If value does not have shape (3,).

        Notes:
            This method updates the robot's internal velocity.
        """
        if not isinstance(value, np.ndarray):
            raise TypeError("velocity must be a NumPy array.")

        if value.shape != (3,):
            raise ValueError("velocity must have shape (3,).")

        self._velocity = value.copy()

    @property
    def telemetry(self) -> dict:
        """Return the robot's current telemetry.

        Returns:
            dict: A dictionary containing the robot's current pose,
                battery charge, and operational status. The dictionary
                has the following keys:
                - "pose": Current pose as a NumPy array.
                - "velocity": Current velocity as a NumPy array.
                - "charge": Current battery charge as a percentage.
                - "status": Current operational status as a RobotStatus.
        """
        return {
            "pose": self.pose,
            "velocity": self.velocity,
            "charge": self.charge,
            "status": self.status,
        }
        
    @property
    def use_rate(self) -> float:
        """Return the robot's charge use rate per meter traveled.

        Returns:
            float: The charge use rate in percentage per meter.

        Notes:
            This value is derived from the robot's configuration and
            represents how much battery charge is consumed for each
            meter the robot travels.
        """
        return self.config.charge_use_rate_per_meter

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