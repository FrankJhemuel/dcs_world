from copy import copy

from dcs_world.geometry.pose import Position
from dcs_world.observation import RobotObservation

class DroneObservation(RobotObservation):
    """Represent the observations collected by a drone."""
    
    @staticmethod
    def generate_poi_observation(timestamp: float, position: Position) -> dict:
        """Generate a point of interest (POI) observation."""
        return {
            "timestamp": timestamp,
            "type": "poi",
            "position": copy(position)
        }