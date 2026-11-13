from dataclasses import dataclass, asdict
import json
from typing import Literal

from dcs_world.geometry.position import Position

@dataclass
class RobotObservation():
    """Base class for robot observations."""
    timestamp: float
    type: Literal["obstacle"]
    position: Position
    
    def to_dict(self) -> dict:
        data = asdict(self)
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict())