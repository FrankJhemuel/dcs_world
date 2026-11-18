from dataclasses import dataclass, fields

from dcs_world.communication.messages import POIMessage
from dcs_world.geometry.position import Position


@dataclass
class POIModel:
    """Represent the observations collected by a robot regarding points of interest."""

    building_position: Position
    
    
    @classmethod
    def from_status_message(cls, message: POIMessage):
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