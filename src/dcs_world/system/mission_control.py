from dcs_world.geometry import Position
from dcs_world.robot.utils.deployment_state import DeploymentState
from dcs_world.robot.utils.robot_status import RobotStatus
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
            robot_id: robot
            for robot_id, robot in self.all_robots.items()
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
            robot_id: robot
            for robot_id, robot in self.all_robots.items()
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
            robot_id: robot
            for robot_id, robot in stored_robots.items()
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

    def get_drone(self, robot_id: str) -> RobotModel | None:
        """Retrieve a registered drone by its ID."""

        return self.drones.get(robot_id)

    def get_ground_robot(self, robot_id: str) -> RobotModel | None:
        """Retrieve a registered ground robot by its ID."""

        return self.ground_robots.get(robot_id)

    def update_robot(
        self,
        robot_id: str,
        updated_robot: RobotModel
    ) -> None:
        """Update the registered model of an existing robot."""

        if not isinstance(updated_robot, RobotModel):
            raise TypeError("Expected a RobotModel instance.")

        if updated_robot.robot_type == "Drone":
            if robot_id not in self.drones:
                raise ValueError(f"Drone with ID {robot_id} does not exist.")

            self.drones[robot_id] = updated_robot

        elif updated_robot.robot_type == "GroundRobot":
            if robot_id not in self.ground_robots:
                raise ValueError(
                    f"Ground robot with ID {robot_id} does not exist."
                )

            self.ground_robots[robot_id] = updated_robot

        else:
            raise ValueError(
                "Invalid robot type. Must be 'Drone' or 'GroundRobot'."
            )

    # ================================================================
    # ENVIRONMENT MODEL - MAP GENERATION
    # ================================================================

    def generate_map(
        self,
        seed: int | None = None,
    ) -> None:
        """Generate the environment map using the specified parameters."""

        self.map.generate_map(
            seed=seed
        )

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