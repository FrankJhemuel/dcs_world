from enum import Enum, auto

class TaskStatus(Enum):
    IDLE = auto()
    ASSIGNED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()