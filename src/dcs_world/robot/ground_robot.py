from dcs_world.geometry.pose import Pose

from .robot import Robot
from .utils import RobotConfig


class GroundRobot(Robot):
    """Represent a ground robot in the simulated world."""

    def __init__(
        self,
        init_pose: Pose | None = None,
        init_soc: float = 100.0,
        config: RobotConfig = Robot.DEFAULT_CONFIG,
    ) -> None:
        """Initialize the ground robot with its initial state and configuration.

        Args:
            init_x (float): Initial x-coordinate of the ground robot.
            init_y (float): Initial y-coordinate of the ground robot.
            init_yaw (float): Initial orientation in radians.
            init_soc (float): Initial state of charge as a percentage
                between 0 and 100.
            config (RobotConfig): Configuration parameters of the ground robot.

        Raises:
            TypeError: If a numeric parameter has an invalid type or config
                is not a RobotConfig instance.
            ValueError: If the initial battery charge is outside the range
                [0, 100] or the configuration is invalid.
        """
        super().__init__(
            init_pose=init_pose,
            init_soc=init_soc,
            config=config,
        )
        