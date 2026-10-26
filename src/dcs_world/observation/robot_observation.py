import copy

from dcs_world.geometry.pose import Position

class RobotObservation():
    """Base class for robot observations."""
    
    @staticmethod
    def generate_obstacle_observation(timestamp: float, position: Position) -> dict:
        """Generate an obstacle observation."""
        return {
            "timestamp": timestamp,
            "type": "obstacle",
            "obstacle": copy(position)
        }