from dcs_world.geometry import Position

class RoadNetwork:
    """Road graph representation for a road network in DCS World."""
    
    def __init__(self, road_intersections: list[Position] = []):
        self.road_intersections : list[Position] = road_intersections

    def add_intersection(self, intersection: Position):
        """Add an intersection to the network."""
        self.road_intersections.append(intersection)

    def get_intersections(self) -> list[Position]:
        """Return the list of intersections in the network."""
        return self.road_intersections