from dataclasses import dataclass


@dataclass
class Vector3:
    """Represent a three-dimensional vector."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def copy(self) -> "Vector3":
        return Vector3(
            x=self.x,
            y=self.y,
            z=self.z,
        )