from copy import copy

from .robot import Robot
from .robot_utils import RobotConfig
from dcs_world.geometry.pose import Position


class GroundRobot(Robot):
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

        self.observations: dict[str, list[Position]] = {
            "civilians": []
        }
        
        self.num_of_civ_per_location: dict[tuple[float, float], int] = {}
        

    def update_observations(
        self,
        new_observations: dict[str, list[Position]],
    ) -> None:
        """Update the ground robot's observations with newly detected positions.

        Args:
            new_observations (dict[str, list[Position]]): Dictionary mapping
                observation categories to lists of observed positions.

        Raises:
            KeyError: If an observation category is not supported by the
                ground robot's observations dictionary.

        Notes:
            The ground robot's observations are updated by replacing the
            existing lists of observed positions with the new ones provided.
        """
        for key, positions in new_observations.items():
                    if key not in self.observations:
                        raise KeyError(f"Unknown observation category: {key}")
        
                    for position in positions:
                        if position not in self.observations[key]:
                            self.observations[key].append(copy(position))
                            
    def add_civ_observation(self, position: Position, count: int) -> None:
        """Add or update a civilian observation.

        Args:
            position (Position): The position of the observed civilians.
            count (int): The number of civilians observed at this position.

        Notes:
            If the position has not been observed before, it is added to the
            observations list and its civilian count is initialized.
            Otherwise, the new count is added to the existing count.
        """
        if position not in self.observations["civilians"]:
            self.observations["civilians"].append(copy(position))
            self.num_of_civ_per_location[(position.x, position.y)] = count
        else:
            self.num_of_civ_per_location[(position.x, position.y)] += count