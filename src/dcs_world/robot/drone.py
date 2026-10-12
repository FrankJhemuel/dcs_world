from copy import copy

from .robot import Robot
from .robot_utils import RobotConfig
from dcs_world.geometry.pose import Position

class Drone(Robot):
    """Represent a drone in the simulated world.

    Attributes:
        observations (dict[str, list[Position]]): Observed positions grouped
            by category. Supported categories are:
            - "POIs": Points of interest detected by the drone.
            - "obstacles": Obstacles detected by the drone.
    """

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

        Notes:
            The initial state and configuration are initialized by the
            Robot base class. The drone's observation categories are
            initialized with empty lists.
        """
        super().__init__(
            init_x=init_x,
            init_y=init_y,
            init_yaw=init_yaw,
            init_charge=init_charge,
            config=config,
        )

        self.observations: dict[str, list[Position]] = {
            "POIs": [],
            "obstacles": [],
        }

    def update_observations(
        self,
        new_observations: dict[str, list[Position]],
    ) -> None:
        """Update the drone's observations with newly detected positions.

        Args:
            new_observations (dict[str, list[Position]]): Dictionary mapping
                observation categories to lists of observed positions.

        Raises:
            KeyError: If an observation category is not supported by the
                drone's observations dictionary.

        Notes:
            Only positions not already present in their respective
            categories are added. Each new position is copied before
            being stored to avoid sharing object references.
        """
        for key, positions in new_observations.items():
            if key not in self.observations:
                raise KeyError(f"Unknown observation category: {key}")

            for position in positions:
                if position not in self.observations[key]:
                    self.observations[key].append(copy(position))
                    
    def add_POI_observation(self, position: Position) -> None:
        """Add a point of interest (POI) observation.

        Args:
            position (Position): Position of the observed point of interest.

        Notes:
            The position is added only if it is not already present in the
            POI observations. A copy is stored to avoid sharing object
            references.
        """
        if position not in self.observations["POIs"]:
            self.observations["POIs"].append(copy(position))

    def add_obstacle_observation(self, position: Position) -> None:
        """Add an obstacle observation.

        Args:
            position (Position): Position of the observed obstacle.

        Notes:
            The position is added only if it is not already present in the
            obstacle observations. A copy is stored to avoid sharing object
            references.
        """
        if position not in self.observations["obstacles"]:
            self.observations["obstacles"].append(copy(position))