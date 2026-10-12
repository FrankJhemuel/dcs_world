from dataclasses import dataclass
import numpy as np

from .position import Position

@dataclass
class Pose(Position):
    """_summary_

    Attributes:
        Position (_type_): The base position of the pose.
        yaw (float): The orientation of the pose in radians.
    """
    yaw: float
    
    @property
    def as_np_array(self) -> np.ndarray:
        """Return the pose as a NumPy array.

        Returns:
            np.ndarray: A 1D array containing the x, y coordinates and yaw.
        """
        return np.array([self.x, self.y, self.yaw])
    
    @as_np_array.setter
    def as_np_array(self, value: np.ndarray) -> None:
        """Set the pose from a NumPy array.

        Args:
            value: Array containing [x, y, yaw].

        Raises:
            TypeError: If value is not a NumPy array or contains
                non-numeric values.
            ValueError: If the array has an invalid shape or contains
                non-finite values.
        """
        if not isinstance(value, np.ndarray):
            raise TypeError("Pose array must be a NumPy ndarray.")

        if value.shape != (3,):
            raise ValueError("Pose array must have shape (3,).")

        if not np.issubdtype(value.dtype, np.number):
            raise TypeError("Pose array must contain numeric values.")

        if not np.all(np.isfinite(value)):
            raise ValueError("Pose array must contain only finite values.")

        self.x, self.y, self.yaw = map(float, value)