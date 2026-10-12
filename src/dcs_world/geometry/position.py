from dataclasses import dataclass
import numpy as np

@dataclass
class Position():
    """Represents a position in 2D space.

    Attributes:
        x (float): The x-coordinate of the position.
        y (float): The y-coordinate of the position.
    """
    x: float
    y: float

    @property
    def as_np_array(self) -> np.ndarray:
        """Return the position as a NumPy array.

        Returns:
            np.ndarray: A 1D array containing the x and y coordinates.
        """
        return np.array([self.x, self.y])
    
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

        if value.shape != (2,):
            raise ValueError("Pose array must have shape (2,).")

        if not np.issubdtype(value.dtype, np.number):
            raise TypeError("Pose array must contain numeric values.")

        if not np.all(np.isfinite(value)):
            raise ValueError("Pose array must contain only finite values.")

        self.x, self.y, self.yaw = map(float, value)