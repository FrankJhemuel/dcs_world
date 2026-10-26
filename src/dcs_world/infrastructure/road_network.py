from dcs_world.geometry import Position

class RoadNetwork:
    """Road graph representation for a road network in DCS World."""
    
    def __init__(self, roads: list[tuple[Position, Position]] = []):
        self.roads : list[tuple[Position, Position]] = roads

    def add_road(self, road: tuple[Position, Position]):
        """Add a road to the network."""
        self.roads.append(road)

    def get_roads(self) -> list[tuple[Position, Position]]:
        """Return the list of roads in the network."""
        return self.roads