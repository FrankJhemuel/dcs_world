from dataclasses import dataclass, fields

from dcs_world.communication.messages import CivilianMessage
from dcs_world.geometry.position import Position


@dataclass
class CivilianModel:
    """Represent the observations collected by a civilian."""

    building_position: Position
    n_civilians: int
    
    @classmethod
    def from_status_message(cls, message: CivilianMessage):
        """Create a RobotModel from a RobotStatusMessage."""
        if message is None:
            raise ValueError("message cannot be None.")
        
        model_fields = {
            field.name
            for field in fields(cls)
        }

        values = {
            name: getattr(message, name)
            for name in model_fields
        }

        return cls(**values)