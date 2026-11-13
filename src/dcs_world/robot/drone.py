from dcs_world.geometry.pose import Pose

from .robot import Robot
from .utils import RobotConfig


class Drone(Robot):
    """Represent a drone in the simulated world."""

    def __init__(
        self,
        init_pose: Pose | None = None,
        init_soc: float = 100.0,
        config: RobotConfig = Robot.DEFAULT_CONFIG,
    ) -> None:
        """Initialize the drone with its initial state and configuration.

        Args:
            init_x: Initial x-coordinate of the drone.
            init_y: Initial y-coordinate of the drone.
            init_yaw: Initial orientation in radians.
            init_soc: Initial state of charge as a percentage
                between 0 and 100.
            config: Configuration parameters of the drone.

        Notes:
            The initial state and configuration are handled by the Robot
            base class. The drone's observations are initialized using
            a DroneObservations instance.
        """
        super().__init__(
            init_pose=init_pose,
            init_soc=init_soc,
            config=config,
        )