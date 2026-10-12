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