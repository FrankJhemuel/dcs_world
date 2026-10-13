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

        self.observations: dict[
            str,
            list[Position] | dict[tuple[float, float], int],
        ] = {
            "buildings": [],
            "n_civilians": {},
        }

    def update_observations(
        self,
        new_observations: dict[
            str,
            list[Position] | dict[tuple[float, float], int],
        ],
    ) -> None:
        """Update the ground robot's observations with newly detected data.

        Args:
            new_observations: Dictionary mapping observation categories to
                lists of building positions or dictionaries of civilian counts.

        Raises:
            KeyError: If an observation category is not supported.
            TypeError: If the observation data has an invalid type.

        Notes:
            New positions are added only if they have not already been
            observed. Existing civilian counts are incremented when the
            same coordinates are observed again.
        """
        for key, data in new_observations.items():
            if key not in self.observations:
                raise KeyError(f"Unknown observation category: {key}")

            if key == "buildings":
                if not isinstance(data, list):
                    raise TypeError(
                        "'buildings' observations must be a list of Position objects."
                    )
                for position in data:
                    if not isinstance(position, Position):
                        raise TypeError(
                            "Each building observation must be a Position."
                        )
                    if position not in self.observations["buildings"]:
                        self.observations["buildings"].append(copy(position))
            elif key == "n_civilians":
                if not isinstance(data, dict):
                    raise TypeError(
                        "'n_civilians' observations must be a dictionary."
                    )

                n_civilians = self.observations["n_civilians"]

                for coordinates, count in data.items():
                    if coordinates not in n_civilians:
                        n_civilians[coordinates] = count
                    else:
                        n_civilians[coordinates] += count

    def add_civ_observation(
        self,
        position: Position,
        count: int,
    ) -> None:
        """Add or update a civilian observation.

        Args:
            position (Position): Position of buildings that contained civilians.
            count (int): Number of civilians observed at this building.

        Notes:
            If the position has not been observed before, it is added to the
            observations list and its civilian count is initialized.
            Otherwise, the existing civilian count is incremented.
        """
        buildings = self.observations["buildings"]
        n_civilians = self.observations["n_civilians"]

        coordinates = (position.x, position.y)

        if position not in buildings:
            buildings.append(copy(position))
            n_civilians[coordinates] = count
        else:
            n_civilians[coordinates] += count
