from dataclasses import dataclass
from .vector3 import Vector3

@dataclass
class Pose:
    """_summary_

    Attributes:
        Position (_type_): The base position of the pose.
        yaw (float): The orientation of the pose in radians.
    """
    position: Vector3
    orientation: Vector3  # Assuming orientation is represented as a Vector3 for roll, pitch, yaw
    
    @property
    def x(self) -> float:
        """Get the x-coordinate of the position.

        Returns:
            float: The x-coordinate of the position.
        """
        return self.position.x

    @property
    def y(self) -> float:
        """Get the y-coordinate of the position.

        Returns:
            float: The y-coordinate of the position.
        """
        return self.position.y

    @property
    def z(self) -> float:
        """Get the z-coordinate of the position.

        Returns:
            float: The z-coordinate of the position.
        """
        return self.position.z

    @property
    def yaw(self) -> float:
        """Get the yaw (rotation around the Z-axis) from the orientation.

        Returns:
            float: The yaw angle in radians.
        """
        return self.orientation.z
    
    @x.setter
    def x(self, value: float) -> None:
        """Set the x-coordinate of the position.

        Args:
            value (float): The new x-coordinate of the position.
        """
        self.position.x = value
        
    @y.setter
    def y(self, value: float) -> None:
        """Set the y-coordinate of the position.

        Args:
            value (float): The new y-coordinate of the position.
        """
        self.position.y = value
    
    @z.setter
    def z(self, value: float) -> None:
        """Set the z-coordinate of the position.

        Args:
            value (float): The new z-coordinate of the position.
        """
        self.position.z = value
    
    @yaw.setter
    def yaw(self, value: float) -> None:
        """Set the yaw (rotation around the Z-axis) in the orientation.

        Args:
            value (float): The new yaw angle in radians.
        """
        self.orientation.z = value
    
    @classmethod
    def from_coordinates(cls, x: float = 0.0, y: float = 0.0, z: float = 0.0, yaw: float = 0.0) -> 'Pose':
        """Create a Pose instance from individual coordinates and yaw.

        Args:
            x (float): The x-coordinate of the position.
            y (float): The y-coordinate of the position.
            z (float): The z-coordinate of the position.
            yaw (float): The yaw angle in radians.

        Returns:
            Pose: A new instance of Pose with the specified position and orientation.
        """
        position = Vector3(x, y, z)
        orientation = Vector3(0.0, 0.0, yaw)  # Assuming roll and pitch are zero
        return cls(position=position, orientation=orientation)
    
    def copy(self) -> 'Pose':
        """Create a copy of the current Pose instance.

        Returns:
            Pose: A new instance of Pose with the same position and orientation as the current instance.
        """
        return Pose(position=self.position, orientation=self.orientation)