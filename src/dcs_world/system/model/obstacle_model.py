from dataclasses import dataclass, fields

from dcs_world.geometry.position import Position

@dataclass
class ObstacleModel:
    """Represent the observations collected by a robot regarding obstacles."""

    timestamp: float
    position: Position
    
    @classmethod
    def from_status_message(cls, message: 'ObstacleMessage') -> 'ObstacleModel': #type: ignore
        """Create a ObstacleModel from a ObstacleMessage."""
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