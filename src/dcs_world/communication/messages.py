from dataclasses import dataclass
from dcs_world.geometry.twist import Twist

@dataclass
class TwistStamped:
    """Represent a velocity command with a timestamp."""

    timestamp: float
    twist: Twist