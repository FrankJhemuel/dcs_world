import math

from dcs_world.geometry import Position
from dcs_world.geometry.pose import Pose
from dcs_world.robot.utils.deployment_state import DeploymentState
from dcs_world.robot.utils.robot_status import RobotStatus
from dcs_world.robot.utils.task_status import TaskStatus
from dcs_world.system.model.civilian_model import CivilianModel
from dcs_world.system.model.obstacle_model import ObstacleModel
from dcs_world.system.model.poi_model import POIModel
from dcs_world.world import Map
from dcs_world.system.model.robot_model import RobotModel


class MissionControl:
    """Central system for managing robots, missions, and environmental information."""

    def __init__(self):
        """Initialize the mission control system and its managed entities."""

        # ============================================================
        # ROBOT MANAGEMENT
        # ============================================================

        self.drones: dict[str, RobotModel] = {}
        self.ground_robots: dict[str, RobotModel] = {}

        # ============================================================
        # ENVIRONMENT MODEL
        # ============================================================

        self.map = Map()

        # ============================================================
        # ENVIRONMENTAL OBSERVATIONS
        # ============================================================

        self.civilians: list[CivilianModel] = []
        self.obstacles: list[ObstacleModel] = []
        self.pois: list[POIModel] = []

    # ================================================================
    # MISSION CONTROL
    # ================================================================

    @property
    def all_robots(self) -> dict[str, RobotModel]:
        """Return a combined dictionary containing all registered robots."""

        return {
            **self.drones,
            **self.ground_robots
        }

    @property
    def points_of_interest(self) -> list[POIModel]:
        """Return all registered points of interest."""

        return self.pois

    # ===============================================================
    # ROBOT MANAGEMENT - TASKS
    # ================================================================
    
    def get_available_robots_for_task(
        self,
        robot_type: str | None = None
    ) -> dict[str, RobotModel]:
        """Return deployed robots that can accept a new task."""

        self._validate_robot_type(robot_type)

        available_task_states = (
            TaskStatus.IDLE,
            TaskStatus.COMPLETED,
            TaskStatus.FAILED
        )

        return {
            robot_id: robot
            for robot_id, robot in self.all_robots.items()
            if robot.deployment_state == DeploymentState.DEPLOYED
            and robot.status not in (
                RobotStatus.CHARGING,
                RobotStatus.ERROR
            )
            and robot.task_status in available_task_states
            and (robot_type is None or robot.robot_type == robot_type)
        }
    
    # ================================================================
    # TASKS
    # ================================================================
    
    # ---------------------------------------------------------------
    # EXPLORATION
    # ---------------------------------------------------------------
    
    def plan_exploration_mission(
        self,
        drone_ids: list[str],
        exploration_area: tuple[float, float, float, float],
    ) -> dict[str, list[Pose]]:

        if not drone_ids:
            raise ValueError("At least one drone must be specified.")

        if len(drone_ids) != len(set(drone_ids)):
            raise ValueError("Drone IDs must be unique.")

        for drone_id in drone_ids:
            if drone_id not in self.drones:
                raise ValueError(f"Drone '{drone_id}' does not exist.")

        # Validate exploration area.
        self.validate_exploration_area(exploration_area)

        # Divide the requested exploration area.
        regions = self.divide_exploration_area(drone_ids, exploration_area)

        # Assign road intersections to each region.
        assignments = self.assign_intersections_to_regions(regions)

        # Convert intersections into Pose waypoints.
        return self.generate_exploration_waypoints(assignments)
    
    def validate_exploration_area(
        self,
        exploration_area: tuple[float, float, float, float],
    ):
        x_min, x_max, y_min, y_max = exploration_area

        map_x_min, map_x_max, map_y_min, map_y_max = self.get_exploration_bounds()

        if x_min >= x_max or y_min >= y_max:
            raise ValueError("Exploration area must have positive dimensions.")

        if (
            x_min < map_x_min
            or x_max > map_x_max
            or y_min < map_y_min
            or y_max > map_y_max
        ):
            raise ValueError("Exploration area must be within map boundaries.")
        
    def get_exploration_bounds(self) -> tuple[float, float, float, float]:
        config = self.map.config

        x_min = 0.0
        x_max = config.cols * config.spacing

        y_min = 0.0
        y_max = config.rows * config.spacing

        return x_min, x_max, y_min, y_max
    
    def divide_exploration_area(
        self,
        drone_ids: list[str],
        exploration_area: tuple[float, float, float, float],
    ) -> dict[str, tuple[float, float, float, float]]:

        if not drone_ids:
            raise ValueError("At least one drone must be specified.")

        x_min, x_max, y_min, y_max = exploration_area

        n = len(drone_ids)

        # Find a grid configuration close to square.
        n_cols = math.ceil(math.sqrt(n))
        n_rows = math.ceil(n / n_cols)

        cell_width = (x_max - x_min) / n_cols
        cell_height = (y_max - y_min) / n_rows

        regions = {}

        for i, drone_id in enumerate(drone_ids):
            row = i // n_cols
            col = i % n_cols

            region_x_min = x_min + col * cell_width
            region_x_max = region_x_min + cell_width

            region_y_min = y_min + row * cell_height
            region_y_max = region_y_min + cell_height

            regions[drone_id] = (
                region_x_min,
                region_x_max,
                region_y_min,
                region_y_max,
            )

        return regions
    
    def assign_intersections_to_regions(
        self,
        regions: dict[str, tuple[float, float, float, float]],
    ) -> dict[str, list[Position]]:

        intersections = self.map.road_network.get_intersections()

        assignments = {drone_id: [] for drone_id in regions}

        for intersection in intersections:
            for drone_id, (x_min, x_max, y_min, y_max) in regions.items():

                inside_x = x_min <= intersection.x < x_max
                inside_y = y_min <= intersection.y < y_max

                # Include the outermost maximum boundaries.
                if x_max == max(r[1] for r in regions.values()):
                    inside_x = x_min <= intersection.x <= x_max

                if y_max == max(r[3] for r in regions.values()):
                    inside_y = y_min <= intersection.y <= y_max

                if inside_x and inside_y:
                    assignments[drone_id].append(intersection)
                    break

        return assignments
    
    def generate_exploration_waypoints(
        self,
        assignments: dict[str, list[Position]],
    ) -> dict[str, list[Pose]]:

        waypoints = {}

        for drone_id, intersections in assignments.items():
            drone = self.get_drone(drone_id)

            altitude = drone.pose.z
            yaw = drone.pose.yaw

            waypoints[drone_id] = [
                Pose.from_coordinates(
                    x=intersection.x,
                    y=intersection.y,
                    z=altitude,
                    yaw=yaw,
                )
                for intersection in intersections
            ]

        return waypoints
    
    # ================================================================
    # ROBOT MANAGEMENT - DEPLOYMENT
    # ================================================================

    def get_stored_robots(
        self,
        robot_type: str | None = None
    ) -> dict[str, RobotModel]:
        """Return stored robots, optionally filtered by robot type."""

        self._validate_robot_type(robot_type)

        return {
            id: robot
            for id, robot in self.all_robots.items()
            if robot.deployment_state == DeploymentState.STORED
            and (robot_type is None or robot.robot_type == robot_type)
        }

    def get_deployed_robots(
        self,
        robot_type: str | None = None
    ) -> dict[str, RobotModel]:
        """Return deployed robots, optionally filtered by robot type."""

        self._validate_robot_type(robot_type)

        return {
            id: robot
            for id, robot in self.all_robots.items()
            if robot.deployment_state == DeploymentState.DEPLOYED
            and (robot_type is None or robot.robot_type == robot_type)
        }

    def get_available_robots(
        self,
        robot_type: str | None = None
    ) -> dict[str, RobotModel]:
        """Return stored robots that are currently available for deployment."""

        self._validate_robot_type(robot_type)

        stored_robots = self.get_stored_robots(robot_type)

        return {
            id: robot
            for id, robot in stored_robots.items()
            if robot.status not in (
                RobotStatus.CHARGING,
                RobotStatus.ERROR
            )
        }

    # ================================================================
    # ROBOT MANAGEMENT - REGISTRATION
    # ================================================================

    def add_drone(self, drone: RobotModel) -> None:
        """Register a drone in the mission control system."""

        if not isinstance(drone, RobotModel) or drone.robot_type != "Drone":
            raise TypeError("Expected a Drone instance.")

        if drone.id in self.drones:
            raise ValueError(f"Drone with ID {drone.id} already exists.")

        self.drones[drone.id] = drone

    def add_ground_robot(self, ground_robot: RobotModel) -> None:
        """Register a ground robot in the mission control system."""

        if (
            not isinstance(ground_robot, RobotModel)
            or ground_robot.robot_type != "GroundRobot"
        ):
            raise TypeError("Expected a GroundRobot instance.")

        if ground_robot.id in self.ground_robots:
            raise ValueError(
                f"Ground robot with ID {ground_robot.id} already exists."
            )

        self.ground_robots[ground_robot.id] = ground_robot

    def get_drone(self, id: str) -> RobotModel | None:
        """Retrieve a registered drone by its ID."""

        return self.drones.get(id)

    def get_ground_robot(self, id: str) -> RobotModel | None:
        """Retrieve a registered ground robot by its ID."""

        return self.ground_robots.get(id)

    def update_robot(
        self,
        id: str,
        updated_robot: RobotModel
    ) -> None:
        """Update the registered model of an existing robot."""

        if not isinstance(updated_robot, RobotModel):
            raise TypeError("Expected a RobotModel instance.")

        if updated_robot.robot_type == "Drone":
            if id not in self.drones:
                raise ValueError(f"Drone with ID {id} does not exist.")

            self.drones[id] = updated_robot

        elif updated_robot.robot_type == "GroundRobot":
            if id not in self.ground_robots:
                raise ValueError(
                    f"Ground robot with ID {id} does not exist."
                )

            self.ground_robots[id] = updated_robot

        else:
            raise ValueError(
                "Invalid robot type. Must be 'Drone' or 'GroundRobot'."
            )

    # ================================================================
    # ENVIRONMENT MODEL - MAP GENERAT
    # ================================================================

    def generate_map(
        self,
        seed: int | None = None,
    ) -> None:
        """Generate the environment map using the specified parameters."""

        self.map.generate_map(
            seed=seed
        )

    def get_exploration_bounds(self) -> tuple[float, float, float, float]:
        config = self.map.config

        x_min = 0.0
        x_max = config.cols * config.spacing

        y_min = 0.0
        y_max = config.rows * config.spacing

        return x_min, x_max, y_min, y_max
    
    # ================================================================
    # ENVIRONMENT MODEL - POINTS OF INTEREST
    # ================================================================

    def add_poi(self, position: Position) -> None:
        """Register a building as a point of interest at the given position."""

        if not isinstance(position, Position):
            raise TypeError("Expected a Position instance.")

        building = self.map.get_building(position)

        if building is None:
            raise ValueError("No building found at the specified position.")

        if building not in self.pois:
            self.pois.append(building)

    # ================================================================
    # ENVIRONMENT MODEL - OBSTACLES
    # ================================================================

    def add_obstacle(self, position: Position) -> None:
        """Register an obstacle at the specified position."""

        if not isinstance(position, Position):
            raise TypeError("Expected a Position instance.")

        if position not in self.obstacles:
            self.obstacles.append(position)

    # ================================================================
    # UTILITIES - VALIDATION
    # ================================================================

    @staticmethod
    def _validate_robot_type(robot_type: str | None) -> None:
        """Validate an optional robot type filter."""

        if robot_type is not None and robot_type not in (
            "Drone",
            "GroundRobot"
        ):
            raise ValueError(
                "robot_type must be 'Drone', 'GroundRobot', or None."
            )