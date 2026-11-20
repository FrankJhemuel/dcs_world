import numpy as np
import uuid

from dcs_world.communication.messages import RobotStatusMessage
from dcs_world.geometry import Pose, Twist, Vector3
from .utils import RobotStatus, RobotConfig


class Robot():
    """Represent an abstract robot in the simulated world.

    Attributes:
        charge (float): Current battery charge as a percentage (0–100).
        status (RobotStatus): Current operational status of the robot.
        config (RobotConfig): Configuration parameters of the robot.
    """

    DEFAULT_CONFIG = RobotConfig(
        max_speed=1.0,
        max_accel=0.5,
        charge_use_rate_per_meter=0.1,
    )
    
    ROBOT_TYPE = "Robot"  # Default robot type; subclasses should override this
    
    def __init__(
        self,
        id: str | None = None,
        init_pose: Pose | None = None,
        init_soc: float = 100.0,
        config: RobotConfig = DEFAULT_CONFIG,
    ) -> None:
        """Initialize the robot's state and configuration.

        Args:
            id (str | None, optional): Unique identifier for the robot.
                Defaults to None, which means a unique ID will be generated.
            init_pose (Pose | None, optional): Initial pose of the robot.
                Defaults to None, which means the robot will be initialized at the origin.
            init_soc (float, optional): Initial state of charge as a
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
            "init_soc": init_soc,
        }

        for name, value in numeric_params.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a numeric value.")
        
        # Validate finite numeric inputs
        if not all(np.isfinite(value) for value in numeric_params.values()):
            raise ValueError("Numeric parameters must be finite.")

        # Validate ranges
        if not 0.0 <= init_soc <= 100.0:
            raise ValueError("Initial state of charge must be between 0 and 100.")

        # Validate configuration
        if config is None:
            raise ValueError("Robot configuration must be provided.")

        if not isinstance(config, RobotConfig):
            raise TypeError("config must be an instance of RobotConfig.")
        
        self.id = str(uuid.uuid4()) if id is None else id  # Unique identifier for the robot
        
        # Initialize state
        if init_pose is None:
            self._pose = Pose(
                x=0.0,
                y=0.0,
                yaw=0.0,
            )
        else:
            self._pose = init_pose
            
        self.soc = float(init_soc)
        self.status = RobotStatus.IDLE

        self._velocity = Twist(
            linear=Vector3(),
            angular=Vector3()
        )  # [vx, vy, omega] in m/s and rad/s
        
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
    def pose(self) -> Pose:
        """Return a copy of the robot's current pose.

        Returns:
            Pose: A Pose object containing the current position and orientation of the robot.

        Notes:
            Returning a copy prevents external modifications from directly
            changing the robot's internal pose.
        """
        return self._pose.copy()

    @property
    def velocity(self) -> Twist:
        """Return a copy of the robot's current velocity.

        Returns:
            Twist: A Twist object containing the current velocity components.

        Notes:
            Returning a copy prevents external modifications from directly
            changing the robot's internal velocity.
        """
        return self._velocity.copy()

    @velocity.setter
    def velocity(self, value: Twist) -> None:
        """Set the robot's current velocity.

        Args:
            value (Twist): A Twist object containing the new velocity components.

        Raises:
            TypeError: If value is not a Twist object.

        Notes:
            This method updates the robot's internal velocity.
        """
        if not isinstance(value, Twist):
            raise TypeError("velocity must be a Twist object.")

        self._velocity = value.copy()
        
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

    def move(self, cmd_vel: Twist, dt: float) -> None:
        """Update robot pose using body-frame velocity commands."""

        # Validate inputs
        if not isinstance(cmd_vel, Twist):
            raise TypeError("cmd_vel must be a Twist object.")

        if isinstance(dt, bool) or not isinstance(dt, (int, float)):
            raise TypeError("dt must be a numeric value.")

        if not np.isfinite(dt) or dt <= 0:
            raise ValueError("dt must be finite and positive.")

        # Current orientation (yaw)
        yaw = self._pose.orientation.z

        # Extract body-frame velocities
        vx_body = cmd_vel.linear.x
        vy_body = cmd_vel.linear.y
        vz_body = cmd_vel.linear.z

        wz = cmd_vel.angular.z

        # Transform body-frame linear velocity into world frame
        rotation_matrix = np.array([
            [np.cos(yaw), -np.sin(yaw)],
            [np.sin(yaw),  np.cos(yaw)]
        ])

        velocity_body = np.array([
            vx_body,
            vy_body
        ])

        velocity_world = rotation_matrix @ velocity_body

        # Integrate position in world frame
        self._pose.position.x += velocity_world[0] * dt
        self._pose.position.y += velocity_world[1] * dt
        self._pose.position.z += vz_body * dt

        # Integrate orientation
        self._pose.orientation.z += wz * dt

        # Keep yaw within [-pi, pi]
        self._pose.orientation.z = np.arctan2(
            np.sin(self._pose.orientation.z),
            np.cos(self._pose.orientation.z)
        )

        # Store commanded velocity
        self._velocity = cmd_vel.copy()  
            
            
            