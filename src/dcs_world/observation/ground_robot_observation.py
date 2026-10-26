from copy import copy

from dcs_world.geometry.pose import Position
from dcs_world.observation import RobotObservation

class GroundRobotObservation(RobotObservation):
    """Represent the observations collected by a ground robot."""

    @staticmethod
    def generate_civilian_observation(timestamp: float, building: Position, n_civilians: int) -> dict:
        """Generate a civilian observation."""
        return {
            "timestamp": timestamp,
            "type": "civilian",
            "building": copy(building),
            "n_civilians": n_civilians
        }