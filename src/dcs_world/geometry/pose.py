from dataclasses import dataclass

from .position import Position

@dataclass
class Pose(Position):
    yaw: float