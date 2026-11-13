from dataclasses import dataclass

from .vector3 import Vector3

@dataclass
class Twist:
    """Represent linear and angular velocity."""

    linear: Vector3
    angular: Vector3