from copy import copy

from dcs_world.geometry.pose import Position
from .robot_observations import RobotObservations


class GroundRobotObservations(RobotObservations):
    """Represent the observations collected by a ground robot.

    Attributes:
        buildings (list[Position]): Unique positions of observed buildings.
        n_civilians (dict[tuple[float, float], int]): Number of civilians
            observed at each (x, y) coordinate.
    """

    def __init__(self) -> None:
        """Initialize empty collections for buildings and civilian counts."""
        self.buildings: list[Position] = []
        self.n_civilians: dict[tuple[float, float], int] = {}

    @property
    def as_dict(
        self,
    ) -> dict[
        str,
        list[Position] | dict[tuple[float, float], int],
    ]:
        """Return the ground robot observations as a dictionary.

        Returns:
            dict: A dictionary containing copies of the building positions
                and civilian count mapping.
        """
        return {
            "buildings": [copy(position) for position in self.buildings],
            "n_civilians": self.n_civilians.copy(),
        }

    def _add_building(self, position: Position) -> None:
        """Add a building observation if its position is not already stored.

        Args:
            position (Position): Position of the observed building.

        Raises:
            TypeError: If position is not a Position instance.

        Notes:
            A copy of the position is stored to prevent external
            modifications from affecting the stored observation.
        """
        if not isinstance(position, Position):
            raise TypeError(
                "position must be a Position instance when adding a building.")
        if position not in self.buildings:
            self.buildings.append(copy(position))

    def add_civilians(self, position: Position, count: int) -> None:
        """Add an observation of civilians at a given position.

        Args:
            position (Position): Position where the civilians were observed.
            count (int): Number of civilians observed, which must be positive.

        Raises:
            TypeError: If position is not a Position instance.
            TypeError: If count is not an integer or is a boolean.
            ValueError: If count is not positive.

        Notes:
            If civilian observations already exist at the given (x, y)
            coordinates, the new count is added to the existing count.
            Otherwise, the position is recorded as a building observation
            and a new civilian count entry is created.
        """
        if not isinstance(position, Position):
            raise TypeError(
                "position must be a Position instance when adding civilians.")
        if not isinstance(count, int) or isinstance(count, bool):
            raise TypeError("count must be an integer when adding civilians.")
        if count <= 0:
            raise ValueError("count must be positive.")

        coordinates = (position.x, position.y)
        if coordinates in self.n_civilians:
            self.n_civilians[coordinates] += count
        else:
            self._add_building(position)
            self.n_civilians[coordinates] = count

    def update(self, new_observations: "GroundRobotObservations") -> None:
        """Merge another set of ground robot observations into this instance.

        Args:
            new_observations (GroundRobotObservations): Observations to merge,
                including building positions and civilian counts.

        Raises:
            TypeError: If new_observations is not a GroundRobotObservations
                instance, or if an observation contains an invalid position
                or civilian count.
            ValueError: If a civilian count is not positive.

        Notes:
            Building positions are added only if they are not already present.
            Civilian counts at matching coordinates are accumulated.
            Positions and counts are processed through the corresponding
            methods to preserve their validation and duplicate-handling rules.
        """
        if not isinstance(new_observations, GroundRobotObservations):
            raise TypeError(
                "new_observations must be a GroundRobotObservations instance."
            )

        for position in new_observations.buildings:
            self._add_building(position)

        for coordinates, count in new_observations.n_civilians.items():
            position = Position(*coordinates)
            self.add_civilians(position, count)
