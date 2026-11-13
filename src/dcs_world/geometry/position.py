from dataclasses import dataclass

@dataclass
class Position():
    """Represents a position in 2D space.

    Attributes:
        x (float): The x-coordinate of the position.
        y (float): The y-coordinate of the position.
    """
    x: float
    y: float
        
    def __hash__(self):
        """Compute a hash value for the Position instance.

        Returns:
            int: A hash value based on the x and y coordinates.
        """
        return hash((self.x, self.y))