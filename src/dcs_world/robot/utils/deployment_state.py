from enum import Enum, auto

class DeploymentState(Enum):
    STORED = auto()
    DEPLOYED = auto()
    RETURNING = auto()