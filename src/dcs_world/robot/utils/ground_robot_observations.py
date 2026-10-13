from dcs_world.geometry.pose import Position
from .robot_observations import RobotObservations


class GroundRobotObservations(RobotObservations):
    """Represent the observations made by a ground robot.
    """
    
    def __init__(self) -> None:
        """Initialize the ground robot observations."""
        
        
        self.buildings: list[Position] = []
        self.n_civilians: dict[tuple[float, float], int] = {}

    @property
    def as_dict(
        self,
    ) -> dict[
        str,
        list[Position] | dict[tuple[float, float], int],
    ]:
        """Return the ground robot observations as a dictionary."""
        return {
            "buildings": self.buildings,
            "n_civilians": self.n_civilians,
        }

    def add_building(self, position: Position) -> None:
        """Add a building if it has not already been observed."""
        if position not in self.buildings:
            self.buildings.append(position)

    def add_civilians(self, position: Position, count: int) -> None:
        """Accumulate the number of civilians observed at a position."""
        self.add_building(position)

        coordinates = (position.x, position.y)
        self.n_civilians[coordinates] = (
            self.n_civilians.get(coordinates, 0) + count
        )

    def update(self, new_observations: "GroundRobotObservations") -> None:
        """Merge another set of ground robot observations.

        Args:
            new_observations: Ground robot observations to merge.

        Raises:
            TypeError: If the input is not a GroundRobotObservations instance.
        """
        if not isinstance(new_observations, GroundRobotObservations):
            raise TypeError(
                "new_observations must be a GroundRobotObservations instance."
            )

        for position in new_observations.buildings:
            self.add_building(position)

        for coordinates, count in new_observations.n_civilians.items():
            position = Position(*coordinates)
            self.add_civilians(position, count)