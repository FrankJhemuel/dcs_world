from dataclasses import dataclass

from .position import Position

@dataclass
class Pose(Position):
    """_summary_

    Attributes:
        Position (_type_): The base position of the pose.
        yaw (float): The orientation of the pose in radians.
    """
    yaw: float
    
    def to_json(self) -> dict:
        """Convert the Pose instance to a JSON-serializable dictionary.

        Returns:
            dict: A dictionary representation of the Pose instance with keys
                "x", "y", and "yaw".
        """
        return {
            "x": self.x,
            "y": self.y,
            "yaw": self.yaw,
        }