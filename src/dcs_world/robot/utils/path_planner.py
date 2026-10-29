import heapq
import itertools
import math

from dcs_world.geometry import Position
from dcs_world.infrastructure import RoadNetwork


class PathPlanner:
    """Plan paths through a road network using A*."""

    def __init__(self, road_network: RoadNetwork):
        self.obstacles: list[Position] = []
        self.road_network = road_network

    @staticmethod
    def distance(a: Position, b: Position) -> float:
        """Calculate horizontal Euclidean distance between two positions."""
        return math.hypot(a.x - b.x, a.z - b.z)

    def add_obstacle(self, obstacle: Position):
        """Add an obstacle to the environment."""
        self.obstacles.append(obstacle)

    def remove_obstacle(self, obstacle: Position):
        """Remove an obstacle from the environment."""
        self.obstacles.remove(obstacle)

    def is_road_blocked(self, start: Position, end: Position) -> bool:
        """Check whether an obstacle lies between two road intersections."""
        return any(
            self._is_between(obstacle, start, end)
            for obstacle in self.obstacles
        )

    @staticmethod
    def _is_between(
        obstacle: Position,
        start: Position,
        end: Position,
    ) -> bool:
        """Check whether an obstacle lies on the segment between two positions."""
        dx = end.x - start.x
        dz = end.z - start.z

        ox = obstacle.x - start.x
        oz = obstacle.z - start.z

        # Check whether the obstacle lies on the same line as the road.
        cross_product = dx * oz - dz * ox

        if not math.isclose(cross_product, 0.0, abs_tol=1e-6):
            return False

        # Check whether the obstacle lies strictly between the endpoints.
        dot_product = ox * dx + oz * dz
        length_squared = dx * dx + dz * dz

        return 0 < dot_product < length_squared

    def plan_path(
        self,
        start: Position,
        goal: Position,
    ) -> list[Position] | None:
        """Find the shortest unblocked road route using A*."""

        # Ensure the start and goal are valid intersections in the road network.
        if start not in self.road_network.roads:
            raise ValueError("Start position is not a road intersection.")

        if goal not in self.road_network.roads:
            raise ValueError("Goal position is not a road intersection.")

        # Generate unique counter values to break ties in the priority queue
        # without comparing Position objects when costs are equal.
        counter = itertools.count()

        # Initialize the priority queue with the starting intersection.
        # Each entry contains (f_score, g_score, counter, position):
        #   f_score: estimated total cost from start to goal through this node.
        #   g_score: actual cost of reaching this node from the start.
        #   counter: unique value used to break ties.
        #   position: the intersection being explored.
        open_set = [
            (self.distance(start, goal), 0.0, next(counter), start)
        ]

        # Store the predecessor of each intersection to reconstruct the path.
        came_from: dict[Position, Position] = {}

        # Store the lowest known cost from the start to each intersection.
        # The starting intersection has a cost of zero.
        g_score: dict[Position, float] = {start: 0.0}

        # Track intersections that have already been fully explored.
        closed_set: set[Position] = set()

        # Continue searching while there are intersections left to explore.
        while open_set:

            # Retrieve the intersection with the lowest estimated total cost.
            _, current_g, _, current = heapq.heappop(open_set)

            # Skip outdated queue entries if a better route to this intersection
            # has already been discovered.
            if current_g != g_score.get(current, math.inf):
                continue

            # If the goal is reached, reconstruct the route by following
            # predecessor links backward from the goal to the start.
            if current == goal:
                path = [current]

                while current in came_from:
                    current = came_from[current]
                    path.append(current)

                # Reverse the path so that it runs from start to goal.
                return path[::-1]

            # Skip intersections that have already been explored.
            if current in closed_set:
                continue

            # Mark the current intersection as explored.
            closed_set.add(current)

            # Examine all intersections directly connected to the current one.
            for neighbor in self.road_network.get_neighbors(current):

                # Ignore neighbors that have already been explored.
                if neighbor in closed_set:
                    continue

                # Ignore roads blocked by obstacles.
                if self.is_road_blocked(current, neighbor):
                    continue

                # Calculate the cost of reaching the neighbor through the current
                # intersection: current path cost + distance along this road.
                tentative_g = (
                    g_score[current]
                    + self.distance(current, neighbor)
                )

                # Update the neighbor only if this route improves its best-known
                # cost. Unvisited neighbors have an initial cost of infinity.
                if tentative_g < g_score.get(neighbor, math.inf):

                    # Record the current intersection as the neighbor's predecessor.
                    came_from[neighbor] = current

                    # Update the lowest known cost from the start to the neighbor.
                    g_score[neighbor] = tentative_g

                    # Estimate the total route cost using:
                    # f(n) = g(n) + h(n)
                    # g(n): actual cost from the start to the neighbor.
                    # h(n): Euclidean distance from the neighbor to the goal.
                    f_score = (
                        tentative_g
                        + self.distance(neighbor, goal)
                    )

                    # Add the neighbor to the priority queue.
                    # A* will prioritize intersections with lower f_score values.
                    heapq.heappush(
                        open_set,
                        (
                            f_score,
                            tentative_g,
                            next(counter),
                            neighbor,
                        ),
                    )

        # The queue is empty, so no valid route to the goal exists.
        return None
