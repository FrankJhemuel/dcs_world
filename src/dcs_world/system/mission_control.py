from dcs_world.geometry import Position
from dcs_world.system.model.civilian_model import CivilianModel
from dcs_world.system.model.obstacle_model import ObstacleModel
from dcs_world.system.model.poi_model import POIModel
from dcs_world.world import Map
from dcs_world.system.model.robot_model import RobotModel


class MissionControl:
    """Mission control system for managing and coordinating missions in DCS World."""

    def __init__(self):
        """Initialize the MissionControl system with empty dictionaries for drones and ground robots, and a map instance."""
        self.drones: dict[str, RobotModel] = {}
        self.ground_robots: dict[str, RobotModel] = {}
        self.map = Map() # Functions as a map model of the mission control
        
        # Observations
        self.civilians: list[CivilianModel] = []
        self.obstacles: list[ObstacleModel] = []
        self.pois: list[POIModel] = []

    # * === MISSION CONTROL ===

    @property
    def all_robots(self) -> dict[str, RobotModel]:
        """Return a combined dictionary of all drones and ground robots."""
        return {**self.drones, **self.ground_robots}

    @property
    def points_of_interest(self) -> list:
        """Return the list of points of interest (POIs) in the mission control system."""
        return self.pois
    
    # * === ROBOTS ===

    def add_drone(self, drone: RobotModel):
        """Add a drone to the mission control system."""
        if not isinstance(drone, RobotModel) or drone.robot_type != "Drone":
            raise TypeError("Expected a Drone instance.")
        if drone.id in self.drones:
            raise ValueError(f"Drone with ID {drone.id} already exists.")
        
        self.drones[drone.id] = drone

    def add_ground_robot(self, ground_robot: RobotModel):
        """Add a ground robot to the mission control system."""
        if not isinstance(ground_robot, RobotModel) or ground_robot.robot_type != "GroundRobot":
            raise TypeError("Expected a GroundRobot instance.")
        if ground_robot.id in self.ground_robots:
            raise ValueError(f"Ground robot with ID {ground_robot.id} already exists.")
        
        self.ground_robots[ground_robot.id] = ground_robot

    def get_drone(self, id: str) -> RobotModel | None:
        """Retrieve a drone by its ID."""
        return self.drones.get(id)

    def get_ground_robot(self, id: str) -> RobotModel | None:
        """Retrieve a ground robot by its ID."""
        return self.ground_robots.get(id)

    def update_robot(self, id: str, updated_robot: RobotModel):
        """Update the information of an existing robot in the mission control system."""
        if not isinstance(updated_robot, RobotModel):
            raise TypeError("Expected a RobotModel instance.")
        
        if updated_robot.robot_type == "Drone":
            if id not in self.drones:
                raise ValueError(f"Drone with ID {id} does not exist.")
            self.drones[id] = updated_robot
        elif updated_robot.robot_type == "GroundRobot":
            if id not in self.ground_robots:
                raise ValueError(f"Ground robot with ID {id} does not exist.")
            self.ground_robots[id] = updated_robot
        else:
            raise ValueError("Invalid robot type. Must be 'Drone' or 'GroundRobot'.")

    # * === MAP ===
    
    def generate_map(
            self,
            seed: int,
            rows: int = 5,
            cols: int = 5,
            spacing: float = 100.0,
            building_probability: float = 0.8,
            obstacle_probability: float = 0.2,
            min_building_size: float = 10.0,
            max_building_size: float = 30.0
            ) -> None:
        """Generate a new map with specified parameters."""
        self.map.generate_map(
            seed=seed,
            rows=rows,
            cols=cols,
            spacing=spacing,
            building_probability=building_probability,
            obstacle_probability=obstacle_probability,
            min_building_size=min_building_size,
            max_building_size=max_building_size
        )

    def add_poi(self, position: Position) -> None:
        """Add a point of interest (POI) to the mission control system."""
        if not isinstance(position, Position):
            raise TypeError("Expected a Position instance.")

        building = self.map.get_building(position)
        if building is None:
            raise ValueError("No building found at the specified position.")

        if building not in self.pois:
            self.pois.append(building)
            
    def add_obstacle(self, position: Position) -> None:
        """Add an obstacle to the mission control system."""
        if not isinstance(position, Position):
            raise TypeError("Expected a Position instance.")

        if position not in self.obstacles:
            self.obstacles.append(position)
            
        