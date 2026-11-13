from dataclasses import dataclass

from .vector3 import Vector3

@dataclass
class Twist:
    """Represent linear and angular velocity."""

    linear: Vector3
    angular: Vector3

    def __post_init__(self):
        """Convert list or tuple inputs into Vector3 instances."""

        if isinstance(self.linear, (list, tuple)):
            self.linear = Vector3(*self.linear)

        if isinstance(self.angular, (list, tuple)):
            self.angular = Vector3(*self.angular)

    def copy(self) -> 'Twist':
        """Create a copy of the Twist instance."""

        return Twist(
            linear=self.linear,
            angular=self.angular
        )