from dcs_world.infrastructure import Building, RoadNetwork
from dcs_world.geometry import Position


class Map:
    """Map representation for a DCS World scenario, including buildings and road networks."""
    
    def __init__(self):
        self.buildings: list[Building] = []
        self.road_network : RoadNetwork = RoadNetwork()
        self.obstacles: list[Position] = []
        
    def add_building(self, building: Building):
        """Add a building to the map."""
        if not isinstance(building, Building):
            raise TypeError("Expected a Building instance.")
        
        self.buildings.append(building)
        
    def add_road(self, road: tuple[Position, Position]):
        """Add a road to the road network."""
        if not (isinstance(road, tuple) and len(road) == 2 and all(isinstance(pos, Position) for pos in road)):
            raise TypeError("Expected a tuple of two Position instances.")
        
        self.road_network.add_road(road)
        
    def load_road_network(self, roads: list[tuple[Position, Position]] | RoadNetwork):
        """Load a list of roads into the road network."""
        if isinstance(roads, RoadNetwork):
            self.road_network = roads
        elif isinstance(roads, list):
            for road in roads:
                self.add_road(road)
        else:
            raise TypeError("Expected a list of roads or a RoadNetwork instance.")