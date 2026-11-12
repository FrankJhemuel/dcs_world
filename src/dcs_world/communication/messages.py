from dataclasses import dataclass


@dataclass
class Vector3:
    """Represent a three-dimensional vector."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass
class Twist:
    """Represent linear and angular velocity."""

    linear: Vector3
    angular: Vector3


@dataclass
class TwistStamped:
    """Represent a velocity command with a timestamp."""

    timestamp: float
    twist: Twist