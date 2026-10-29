import random

from dcs_world.infrastructure import Building, RoadNetwork
from dcs_world.geometry import Position


class Map:
    """Map representation for a DCS World scenario."""

    def __init__(self):
        self.buildings: list[Building] = []
        self.road_network: RoadNetwork = RoadNetwork()
        self.obstacles: list[Position] = []

    def generate_map(
        self,
        seed: int,
        rows: int = 5,
        cols: int = 5,
        spacing: float = 100.0,
        building_probability: float = 0.8,
        obstacle_probability: float = 0.2,
        min_building_size: float = 10.0,
        max_building_size: float = 30.0,
    ) -> None:
        """
        Generate a stochastic, reproducible grid map.

        Args:
            seed: Random seed for reproducible generation.
            rows: Number of blocks along the y-axis.
            cols: Number of blocks along the x-axis.
            spacing: Distance between adjacent intersections.
            building_probability: Probability of placing a building
                in each block.
            obstacle_probability: Probability of placing an obstacle
                on each road segment.
            min_building_size: Minimum building dimension.
            max_building_size: Maximum building dimension.

        Notes:
            - The road network contains grid intersections.
            - Buildings are placed at block centers.
            - Obstacles are placed along connections between intersections.
            - Existing map contents are replaced.
        """
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

        rng = random.Random(seed)

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

        # Store all intersections in the road network.
        for row in intersections:
            for intersection in row:
                self.add_road_intersection(intersection)

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

        # Generate obstacles along connections between adjacent
        # horizontal intersections.
        for row in range(rows + 1):
            for col in range(cols):
                if rng.random() >= obstacle_probability:
                    continue

                start = intersections[row][col]
                end = intersections[row][col + 1]

                # Avoid placing obstacles directly at intersections.
                t = rng.uniform(0.2, 0.8)

                position = Position(
                    start.x + t * (end.x - start.x),
                    start.y + t * (end.y - start.y),
                )

                self.add_obstacle(position)

        # Generate obstacles along connections between adjacent
        # vertical intersections.
        for row in range(rows):
            for col in range(cols + 1):
                if rng.random() >= obstacle_probability:
                    continue

                start = intersections[row][col]
                end = intersections[row + 1][col]

                t = rng.uniform(0.2, 0.8)

                position = Position(
                    start.x + t * (end.x - start.x),
                    start.y + t * (end.y - start.y),
                )

                self.add_obstacle(position)

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

    def add_obstacle(self, position: Position) -> None:
        """Add an obstacle to the map."""
        if not isinstance(position, Position):
            raise TypeError("Expected a Position instance.")

        self.obstacles.append(position)
