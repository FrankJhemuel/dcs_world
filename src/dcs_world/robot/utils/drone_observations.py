from copy import copy

from dcs_world.geometry.pose import Position
from .robot_observations import RobotObservations


class DroneObservations(RobotObservations):
    def __init__(self) -> None:
        self.pois: list[Position] = []
        self.obstacles: list[Position] = []

    @property
    def as_dict(self) -> dict[str, list[Position]]:
        """Return the drone observations as a dictionary."""
        return {
            "POIs": self.pois,
            "obstacles": self.obstacles,
        }

    def add_poi(self, position: Position) -> None:
        """Add a point of interest if it has not already been observed."""
        if position not in self.pois:
            self.pois.append(copy(position))

    def add_obstacle(self, position: Position) -> None:
        """Add an obstacle if it has not already been observed."""
        if position not in self.obstacles:
            self.obstacles.append(copy(position))

    def update(self, new_observations: "DroneObservations") -> None:
        """Merge another set of drone observations.

        Args:
            new_observations: Drone observations to merge.

        Raises:
            TypeError: If the input is not a DroneObservations instance.
        """
        if not isinstance(new_observations, DroneObservations):
            raise TypeError(
                "new_observations must be a DroneObservations instance."
            )

        for position in new_observations.pois:
            self.add_poi(position)

        for position in new_observations.obstacles:
            self.add_obstacle(position)