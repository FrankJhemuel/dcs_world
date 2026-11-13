from dataclasses import asdict, dataclass
import json
from typing import Literal

from dcs_world.geometry.position import Position

@dataclass
class DroneObservation():
    """Represent the observations collected by a drone."""
    
    timestamp: float
    type: Literal["poi"]
    building_position: Position
    
    def to_dict(self) -> dict:
        data = asdict(self)
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict())