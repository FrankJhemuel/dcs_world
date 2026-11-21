from dataclasses import dataclass
import random

from dcs_world.infrastructure import Building, RoadNetwork
from dcs_world.geometry.position import Position


@dataclass
class MapConfig:
    """Configuration parameters for procedural map generation."""

    seed: int = 42

    rows: int = 5
    cols: int = 5
    spacing: float = 1.0

    building_probability: float = 0.6
    obstacle_probability: float = 0.2

    min_building_size: float = 0.5
    max_building_size: float = 0.5


class Map:
    """Map representation for a DCS World scenario."""

    def __init__(self, config: MapConfig = MapConfig()):
        self.config = config

        self.buildings: list[Building] = []
        self.road_network: RoadNetwork = RoadNetwork()
        self.obstacles: list[Position] = []

    def generate_map(
        self,
        config: MapConfig | None = None,
        seed: int | None = None,
    ) -> None:
        """
        Generate a stochastic, reproducible grid map.

        Args:
            config: Optional configuration parameters for map generation.

        Notes:
            - The road network contains grid intersections and connections.
            - Buildings are placed at block centers.
            - Obstacles are placed along connections between intersections.
            - Existing map contents are replaced.
        """
        if config is not None:
            self.config = config
        if seed is not None:
            self.config.seed = seed

        config = self.config

        seed_ = config.seed
        rows = config.rows
        cols = config.cols
        spacing = config.spacing
        building_probability = config.building_probability
        obstacle_probability = config.obstacle_probability
        min_building_size = config.min_building_size
        max_building_size = config.max_building_size

        if rows < 1 or cols < 1:
            raise ValueError("rows and cols must be positive.")

        if spacing <= 0:
            raise ValueError("spacing must be positive.")

        if not 0.0 <= building_probability <= 1.0:
            raise ValueError(
                "building_probability must be between 0 and 1."
            )

        if not 0.0 <= obstacle_probability <= 1.0:
            raise ValueError(
                "obstacle_probability must be between 0 and 1."
            )

        if not (
            0 < min_building_size <= max_building_size < spacing
        ):
            raise ValueError(
                "Building dimensions must be positive, ordered, "
                "and smaller than the road spacing."
            )

        rng = random.Random(seed_)

        # Reset the map.
        self.buildings.clear()
        self.obstacles.clear()
        self.road_network = RoadNetwork()

        # Generate grid intersections.
        intersections = [
            [
                Position(col * spacing, row * spacing)
                for col in range(cols + 1)
            ]
            for row in range(rows + 1)
        ]

        # Register all intersections in the road network.
        for row in intersections:
            for intersection in row:
                self.road_network.add_intersection(intersection)

        # Connect adjacent horizontal intersections.
        for row in range(rows + 1):
            for col in range(cols):
                self.road_network.connect_intersections(
                    intersections[row][col],
                    intersections[row][col + 1],
                )

        # Connect adjacent vertical intersections.
        for row in range(rows):
            for col in range(cols + 1):
                self.road_network.connect_intersections(
                    intersections[row][col],
                    intersections[row + 1][col],
                )

        # Generate buildings at block centers.
        for row in range(rows):
            for col in range(cols):
                if rng.random() >= building_probability:
                    continue

                center = Position(
                    (col + 0.5) * spacing,
                    (row + 0.5) * spacing,
                )

                # Adapt this constructor to your Building class.
                building = Building(center)
                self.add_building(building)

        # Generate obstacles on horizontal road segments.
        for row in range(rows + 1):
            for col in range(cols):
                if rng.random() >= obstacle_probability:
                    continue

                start = intersections[row][col]
                end = intersections[row][col + 1]

                # Place the obstacle between the intersections.
                t = rng.uniform(0.2, 0.8)

                position = Position(
                    start.x + t * (end.x - start.x),
                    start.y + t * (end.y - start.y),
                )

                self.add_obstacle(position)

        # Generate obstacles on vertical road segments.
        for row in range(rows):
            for col in range(cols + 1):
                if rng.random() >= obstacle_probability:
                    continue

                start = intersections[row][col]
                end = intersections[row + 1][col]

                # Place the obstacle between the intersections.
                t = rng.uniform(0.2, 0.8)

                position = Position(
                    start.x + t * (end.x - start.x),
                    start.y + t * (end.y - start.y),
                )

                self.add_obstacle(position)

    # * === CRUD ===

    # === OBSTACLES ===

    def add_obstacle(self, position: Position) -> None:
        """Add an obstacle to the map."""
        if not isinstance(position, Position):
            raise TypeError("Expected a Position instance.")
        if position not in self.obstacles:
            self.obstacles.append(position)

    # === BUILDINGS ===

    def add_building(self, building: Building) -> None:
        """Add a building to the map."""
        if not isinstance(building, Building):
            raise TypeError("Expected a Building instance.")

        self.buildings.append(building)

    def get_building(self, position: Position) -> Building | None:
        """Retrieve a building at a specific position.

        Args:
            position: The position to check for a building.

        Returns:
            The building at the specified position, or None if no
            building exists there.
        """
        for building in self.buildings:
            if building.position == position:
                return building
        return None

    # === ROAD NETWORK ===

    def add_road_intersection(self, intersection: Position) -> None:
        """Add an intersection to the road network."""
        if not isinstance(intersection, Position):
            raise TypeError("Expected a Position instance.")

        self.road_network.add_intersection(intersection)

    def load_road_network(
        self,
        roads: list[Position] | RoadNetwork,
    ) -> None:
        """Load intersections into the road network."""
        if isinstance(roads, RoadNetwork):
            self.road_network = roads
        elif isinstance(roads, list):
            self.road_network = RoadNetwork()

            for intersection in roads:
                self.add_road_intersection(intersection)
        else:
            raise TypeError(
                "Expected a list of intersections or a RoadNetwork instance."
            )
