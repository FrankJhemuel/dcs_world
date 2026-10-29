from dcs_world.geometry import Position

class RoadNetwork:
    """Road graph representation for a road network in DCS World."""

    def __init__(self, road_intersections: list[Position] | None = None):
        self.road_intersections: list[Position] = road_intersections or []
        self.roads: dict[Position, list[Position]] = {
            node: [] for node in self.road_intersections
        }

    def add_intersection(self, intersection: Position):
        """Add an intersection to the network."""
        if intersection not in self.roads:
            self.road_intersections.append(intersection)
            self.roads[intersection] = []

    def connect_intersections(self, a: Position, b: Position):
        """Connect two intersections with a bidirectional road."""
        self.add_intersection(a)
        self.add_intersection(b)

        if b not in self.roads[a]:
            self.roads[a].append(b)

        if a not in self.roads[b]:
            self.roads[b].append(a)

    def get_intersections(self) -> list[Position]:
        """Return all intersections."""
        return self.road_intersections

    def get_neighbors(self, intersection: Position) -> list[Position]:
        """Return intersections directly connected by roads."""
        return self.roads.get(intersection, [])