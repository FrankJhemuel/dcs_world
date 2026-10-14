from .robot import Robot
from .utils import RobotConfig
from dcs_world.observation import GroundRobotObservations
from dcs_world.geometry.pose import Position


class GroundRobot(Robot):
    """Represent a ground robot in the simulated world."""

    def __init__(
        self,
        init_x: float,
        init_y: float,
        init_yaw: float,
        init_charge: float,
        config: RobotConfig,
    ) -> None:
        """Initialize the ground robot with its initial state and configuration.

        Args:
            init_x (float): Initial x-coordinate of the ground robot.
            init_y (float): Initial y-coordinate of the ground robot.
            init_yaw (float): Initial orientation in radians.
            init_charge (float): Initial battery charge as a percentage
                between 0 and 100.
            config (RobotConfig): Configuration parameters of the ground robot.

        Raises:
            TypeError: If a numeric parameter has an invalid type or config
                is not a RobotConfig instance.
            ValueError: If the initial battery charge is outside the range
                [0, 100] or the configuration is invalid.
        """
        super().__init__(
            init_x=init_x,
            init_y=init_y,
            init_yaw=init_yaw,
            init_charge=init_charge,
            config=config,
        )

        self.observations: GroundRobotObservations = GroundRobotObservations()

    def update_observations(
        self,
        new_observations: GroundRobotObservations,
    ) -> None:
        """Merge newly detected observations into the ground robot's observations."""
        self.observations.update(new_observations)

    def add_civ_observation(
        self,
        position: Position,
        count: int,
    ) -> None:
        """Add or update a civilian observation.

        Args:
            position (Position): Position of the building containing civilians.
            count (int): Number of civilians observed at this building.

        Notes:
            The building is registered if it has not already been observed.
            The civilian count is accumulated at the specified coordinates.
        """
        self.observations.add_civilians(position, count)