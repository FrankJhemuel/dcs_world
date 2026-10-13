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

        if not self.REQUIRED_KEYS.issubset(poi_status.keys()) or len(poi_status) != len(self.REQUIRED_KEYS):
            raise ValueError(
                f"poi_status must be the following keys: {self.REQUIRED_KEYS}"
            )

        self._poi_status = poi_status.copy()

    def update_poi_status(self, key: str, value: int | float | bool) -> None:
        """Update a specific key in the point of interest (POI) status of the building.

        Args:
            key (str): The key in the POI status to update.
            value: The new value for the specified key.
        """
        if key not in self.REQUIRED_KEYS:
            raise ValueError(
                f"Invalid key: {key}. Must be one of {self.REQUIRED_KEYS}")

        if key in ["n_civ", "clear_time"]:
            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"Value for {key} must be an int or float, not {type(value).__name__}.")

            if key == "n_civ" and not isinstance(value, int):
                raise TypeError(
                    f"Value for {key} must be an int, not {type(value).__name__}.")

        if not isinstance(value, bool) and key in ["is_poi", "can_collapse"]:
            raise TypeError(
                f"Value for {key} must be a bool, not {type(value).__name__}.")

        self._poi_status[key] = value

    @staticmethod
    def generate_building_poi_status(is_poi: bool = False, n_civ: int = 0, clear_time: float = 0., can_collapse: bool = False) -> dict:
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
        if not isinstance(is_poi, bool) or not isinstance(can_collapse, bool) or not isinstance(n_civ, int) or not isinstance(clear_time, (int, float)):
            raise TypeError(
                "Invalid types for POI status parameters. Expected types are: is_poi (bool), n_civ (int), clear_time (float), can_collapse (bool).")

        return {
            "is_poi": is_poi,
            "n_civ": n_civ,
            "clear_time": clear_time,
            "can_collapse": can_collapse,
        }
