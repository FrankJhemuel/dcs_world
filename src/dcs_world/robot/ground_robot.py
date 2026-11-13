from dcs_world.geometry.pose import Pose

from .robot import Robot
from .utils import RobotConfig


class GroundRobot(Robot):
    """Represent a ground robot in the simulated world."""

    ROBOT_TYPE = "GroundRobot"
    
    def __init__(
        self,
        id : str | None = None,
        init_pose: Pose | None = None,
        init_soc: float = 100.0,
        config: RobotConfig = Robot.DEFAULT_CONFIG,
    ) -> None:
        """Initialize the ground robot with its initial state and configuration.

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
            TypeError: If a numeric parameter has an invalid type or config
                is not a RobotConfig instance.
            ValueError: If the initial battery charge is outside the range
                [0, 100] or the configuration is invalid.
        """
        super().__init__(
            id=id,
            init_pose=init_pose,
            init_soc=init_soc,
            config=config,
        )
        