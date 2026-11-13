from dataclasses import asdict, dataclass
import json
from typing import Literal

from dcs_world.geometry.pose import Position

@dataclass
class GroundRobotObservation():
    """Represent the observations collected by a ground robot."""
    
    timestamp: float
    type: Literal["civilian"]
    building_position: Position
    n_civilians: int
    

    def to_dict(self) -> dict:
        data = asdict(self)
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict())