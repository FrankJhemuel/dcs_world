from enum import Enum, auto

class RobotStatus(Enum):
    """Represent the possible operational states of a robot."""

    IDLE = auto()
    CHARGING = auto()
    EXECUTING = auto()
    MOVING = auto()
    ERROR = auto()

    # Drone-specific states
    FLYING = auto()
    LANDING = auto()