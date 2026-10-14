from abc import ABC, abstractmethod
from typing import Any


class RobotObservations(ABC):
    """Base class for robot observations."""

    @property
    @abstractmethod
    def as_dict(self) -> dict[str, Any]:
        """Return the observations as a dictionary."""
        pass