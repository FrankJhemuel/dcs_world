from .robot import Robot
from .utils import RobotConfig, DroneObservations
from dcs_world.geometry.pose import Position


class Drone(Robot):
    """Represent a drone in the simulated world."""

    def __init__(
        self,
        init_x: float,
        init_y: float,
        init_yaw: float,
        init_charge: float,
        config: RobotConfig,
    ) -> None:
        """Initialize the drone with its initial state and configuration.

        Args:
            init_x (float): Initial x-coordinate of the drone.
            init_y (float): Initial y-coordinate of the drone.
            init_yaw (float): Initial orientation in radians.
            init_charge (float): Initial battery charge as a percentage
                between 0 and 100.
            config (RobotConfig): Configuration parameters of the drone.

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

        self.observations: DroneObservations = DroneObservations()

    def update_observations(
        self,
        new_observations: DroneObservations,
    ) -> None:
        """Merge newly detected observations into the drone's observations."""
        self.observations.update(new_observations)

    def add_POI_observation(self, position: Position) -> None:
        """Add a point of interest (POI) observation."""
        self.observations.add_poi(position)

    def add_obstacle_observation(self, position: Position) -> None:
        """Add an obstacle observation."""
        self.observations.add_obstacle(position)