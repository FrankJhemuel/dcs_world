from dcs_world.geometry.position import Position


class Building:
    """A class representing a building in the simulated world."""

    REQUIRED_KEYS = frozenset(
        {"is_poi", "n_civ", "clear_time", "can_collapse"})

    def __init__(self, position: Position) -> None:
        """Initialize a building with its position and default point of interest (POI) status.

        Args:
            position (Position): The position of the building in the simulated world.
        """
        if not isinstance(position, Position):
            raise TypeError("position must be a Position instance.")

        self.position: Position = position
        self._poi_status: dict = {
            "is_poi": False,
            "n_civ": 0,
            "clear_time": 0.0,
            "can_collapse": False,
        }

    @classmethod
    def with_poi_status(cls, position: Position, poi_status: dict) -> "Building":
        """Create a building with a specified point of interest (POI) status.

        Args:
            position (Position): The position of the building in the simulated world.
            poi_status (dict): A dictionary containing the POI status of the building.
                Expected keys are "is_poi", "n_civ", "clear_time", and "can_collapse".

        Returns:
            Building: An instance of the Building class with the specified POI status.

        Raises:
            TypeError: If poi_status is not a dictionary.
            ValueError: If poi_status does not contain the required keys.

        Notes:
            You can use the static method `generate_building_poi_status` to create a valid poi_status dictionary.
        """
        building = cls(position)
        building.set_poi_status(poi_status)

        return building

    def set_poi_status(self, poi_status: dict) -> None:
        """Set the point of interest (POI) status of the building.

        Args:
            poi_status (dict): A dictionary containing the POI status of the building.
                Expected keys are "is_poi", "n_civ", "clear_time", and "can_collapse".

        Raises:
            TypeError: If poi_status is not a dictionary.
            ValueError: If poi_status does not contain the required keys.
        """
        if not isinstance(poi_status, dict):
            raise TypeError("poi_status must be a dictionary.")

        if not self.REQUIRED_KEYS.issubset(poi_status.keys()):
            raise ValueError(
                f"poi_status must contain the following keys: {self.REQUIRED_KEYS}"
            )

        self._poi_status = poi_status.copy()

    @staticmethod
    def generate_building_poi_status(is_poi: bool, n_civ: int = 0, clear_time: float = 0., can_collapse: bool = False) -> dict:
        """Generate a dictionary representing the POI status of a building.

        Args:
            is_poi (bool): Whether the building is a point of interest.
            n_civ (int, optional): Number of civilians in the building. Defaults to 0.
            clear_time (float, optional): Time taken to clear the building. Defaults to 0.0.
            can_collapse (bool, optional): Whether the building can collapse. Defaults to False.

        Returns:
            dict: A dictionary containing the POI status of the building.

        Notes:
            This method is useful for creating a valid poi_status dictionary to be used with the `set_poi_status` method or the `with_poi_status` class method.
        """
        return {
            "is_poi": is_poi,
            "n_civ": n_civ,
            "clear_time": clear_time,
            "can_collapse": can_collapse,
        }
