from dcs_world.geometry import Position
from dcs_world.infrastructure import Building
from dcs_world.robot import Drone, GroundRobot
from dcs_world.world import Map


class MissionControl:
    """Mission control system for managing and coordinating missions in DCS World."""

    def __init__(self):
        """Initialize the MissionControl system with empty lists for drones and ground robots, and a map instance."""
        self.drones: list[Drone] = []
        self.ground_robots: list[GroundRobot] = []
        self.map = Map()
        self.observations: dict[str, list[dict]] = {}
        self.pois: list[Building] = []

    # * === MISSION CONTROL ===

    @property
    def all_robots(self) -> list:
        """Return a combined list of all drones and ground robots."""
        return self.drones + self.ground_robots

    @property
    def points_of_interest(self) -> list[Building]:
        """Return the list of points of interest (POIs) in the mission control system."""
        return self.pois

    def get_robot_navigate_to_position_precalc_status(self, robot_id: str, target_position: Position) -> dict:
        """Retrieve the navigation status of a specific robot.

        Args:
            robot_id (str): The unique identifier of the robot.

        Returns:
            dict: A dictionary containing the navigation status of the robot.
                If the robot is not found, returns an empty dictionary.
        """
        robot_obj = None
        for robot in self.all_robots:
            if robot.id == robot_id:
                robot_obj = robot
                break
            
        if robot_obj is None:
            raise ValueError(f"No robot found with ID: {robot_id}")
        
        if isinstance(robot_obj, Drone):
            pass  # Implement drone-specific navigation status retrieval if needed
    
    # * === ROBOTS ===

    def add_drone(self, drone: Drone):
        """Add a drone to the mission control system."""
        if not isinstance(drone, Drone):
            raise TypeError("Expected a Drone instance.")
        self.drones.append(drone)

    def add_ground_robot(self, ground_robot: GroundRobot):
        """Add a ground robot to the mission control system."""
        if not isinstance(ground_robot, GroundRobot):
            raise TypeError("Expected a GroundRobot instance.")
        self.ground_robots.append(ground_robot)

    def get_robot_observations(self) -> None:
        """Retrieve observations from all drones and ground robots.

        Returns:
            dict: A dictionary containing lists of observations from drones
                and ground robots.
        """

        for drone in self.drones:
            if drone.id not in self.observations:
                self.observations[drone.id] = []
            self.observations[drone.id].append(drone.observations)

        for ground_robot in self.ground_robots:
            if ground_robot.id not in self.observations:
                self.observations[ground_robot.id] = []
            self.observations[ground_robot.id].append(
                ground_robot.observations)

        for robot_id, obs_list in self.observations.items():
            for obs in obs_list:
                if obs["type"] == "obstacle":
                    self.add_obstacle_to_map(obs["position"])

                elif obs["type"] == "poi":
                    self.add_poi(obs["position"])
        
        for robot in self.all_robots:
            robot.clear_observations()
        
        self.observations.clear()
                    
    def get_robots_telemetry(self) -> dict:
            """Retrieve telemetry data from all drones and ground robots.
    
            Returns:
                dict: A dictionary containing lists of telemetry data from drones
                    and ground robots.
            """
            telemetry_data = {
                "drones": [drone.telemetry for drone in self.drones],
                "ground_robots": [robot.telemetry for robot in self.ground_robots],
            }
            return telemetry_data

    # * === MAP ===

    def add_obstacle_to_map(self, position):
        """Add an obstacle to the map."""
        self.map.add_obstacle(position)

    def add_poi(self, position: Position) -> None:
        """Add a point of interest (POI) to the mission control system."""
        if not isinstance(position, Position):
            raise TypeError("Expected a Position instance.")

        building = self.map.get_building(position)
        if building is None:
            raise ValueError("No building found at the specified position.")

        if building not in self.pois:
            self.pois.append(building)
