import random

from dcs_world.world import Map


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42

ROWS = 5
COLS = 5
SPACING = 1.0

BUILDING_PROBABILITY = 0.6
OBSTACLE_PROBABILITY = 0.2

ROAD_WIDTH = 0.2
ROAD_HEIGHT = 0.01

BUILDING_MIN_SIZE = 0.5
BUILDING_MAX_SIZE = 0.5
BUILDING_HEIGHT = 1.0

OBSTACLE_SIZE = 0.1

GROUND_HEIGHT = 0.2

# Small offset to avoid Z-fighting between road and ground.
ROAD_CLEARANCE = 0.001

# Keep track of objects created by this script.
generated_objects = []

# CoppeliaSim API module.
sim = None

# Dedicated random generator for visualization.
visual_rng = random.Random(SEED)


# ============================================================
# COPPELIASIM OBJECT CREATION
# ============================================================

def create_box(name, position, size, color):
    """Create a cuboid in the CoppeliaSim scene."""

    handle = sim.createPrimitiveShape(
        sim.primitiveshape_cuboid,
        size,
        0
    )

    sim.setObjectAlias(handle, name)
    sim.setObjectPosition(handle, -1, position)

    sim.setShapeColor(
        handle,
        "",
        sim.colorcomponent_ambient_diffuse,
        color
    )

    generated_objects.append(handle)

    return handle


def clear_generated_objects():
    """Remove objects created by the previous generation."""

    global generated_objects

    for handle in reversed(generated_objects):
        try:
            sim.removeObject(handle)
        except Exception:
            pass

    generated_objects = []


# ============================================================
# ROAD VISUALIZATION
# ============================================================

def create_road(start, end):
    """Create a rectangular road segment between two intersections."""

    dx = end[0] - start[0]
    dy = end[1] - start[1]

    length = (dx**2 + dy**2) ** 0.5

    if length == 0:
        return

    center_x = (start[0] + end[0]) / 2
    center_y = (start[1] + end[1]) / 2

    if abs(dx) >= abs(dy):
        size = [length, ROAD_WIDTH, ROAD_HEIGHT]
    else:
        size = [ROAD_WIDTH, length, ROAD_HEIGHT]

    # The ground is centered at z = 0.
    # Place the road directly on its upper surface, with a tiny clearance.
    ground_top = GROUND_HEIGHT / 2
    road_z = ground_top + ROAD_HEIGHT / 2 + ROAD_CLEARANCE

    create_box(
        "GeneratedMap_Road",
        [center_x, center_y, road_z],
        size,
        [0.15, 0.15, 0.15]
    )


def visualize_roads(world_map):
    """Visualize the road network using row-major intersection order."""

    intersections = world_map.road_network.get_intersections()

    expected_count = (ROWS + 1) * (COLS + 1)

    if len(intersections) != expected_count:
        raise ValueError(
            f"Expected {expected_count} intersections, "
            f"got {len(intersections)}."
        )

    points = [
        [position.x, position.y]
        for position in intersections
    ]

    grid = [
        points[row * (COLS + 1):(row + 1) * (COLS + 1)]
        for row in range(ROWS + 1)
    ]

    # Horizontal connections.
    for row in range(ROWS + 1):
        for col in range(COLS):
            create_road(
                grid[row][col],
                grid[row][col + 1]
            )

    # Vertical connections.
    for row in range(ROWS):
        for col in range(COLS + 1):
            create_road(
                grid[row][col],
                grid[row + 1][col]
            )


# ============================================================
# BUILDING VISUALIZATION
# ============================================================

def visualize_buildings(world_map):
    """Visualize buildings using their generated center positions."""

    for index, building in enumerate(world_map.buildings):
        position = building.position

        width = visual_rng.uniform(
            BUILDING_MIN_SIZE,
            BUILDING_MAX_SIZE
        )

        depth = visual_rng.uniform(
            BUILDING_MIN_SIZE,
            BUILDING_MAX_SIZE
        )

        create_box(
            f"GeneratedMap_Building_{index}",
            [
                position.x,
                position.y,
                BUILDING_HEIGHT / 2
            ],
            [
                width,
                depth,
                BUILDING_HEIGHT
            ],
            [0.65, 0.65, 0.70]
        )


# ============================================================
# OBSTACLE VISUALIZATION
# ============================================================

def visualize_obstacles(world_map):
    """Visualize obstacles standing above the road surface."""

    for index, obstacle in enumerate(world_map.obstacles):
        create_box(
            f"GeneratedMap_Obstacle_{index}",
            [
                obstacle.x,
                obstacle.y,
                GROUND_HEIGHT / 2
                + ROAD_HEIGHT
                + ROAD_CLEARANCE
                + OBSTACLE_SIZE / 2
            ],
            [
                OBSTACLE_SIZE,
                OBSTACLE_SIZE,
                OBSTACLE_SIZE
            ],
            [0.9, 0.15, 0.1]
        )


# ============================================================
# MAP VISUALIZATION
# ============================================================

def visualize_map(world_map):
    """Create the complete map visualization."""

    clear_generated_objects()

    width = COLS * SPACING
    height = ROWS * SPACING

    # Ground centered at z = 0.
    # Its top surface is at z = GROUND_HEIGHT / 2.
    create_box(
        "GeneratedMap_Ground",
        [
            width / 2,
            height / 2,
            0.0
        ],
        [
            width + SPACING,
            height + SPACING,
            GROUND_HEIGHT
        ],
        [0.35, 0.35, 0.35]
    )

    visualize_roads(world_map)
    visualize_buildings(world_map)
    visualize_obstacles(world_map)

    print("Map visualization complete.")
    print(f"Buildings: {len(world_map.buildings)}")
    print(f"Obstacles: {len(world_map.obstacles)}")
    print(f"Scene objects created: {len(generated_objects)}")


# ============================================================
# COPPELIASIM CALLBACKS
# ============================================================

def sysCall_init():
    """Generate and visualize the map when simulation starts."""

    global sim, visual_rng

    sim = require("sim")
    visual_rng = random.Random(SEED)

    world_map = Map()

    world_map.generate_map(
        seed=SEED,
        rows=ROWS,
        cols=COLS,
        spacing=SPACING,
        building_probability=BUILDING_PROBABILITY,
        obstacle_probability=OBSTACLE_PROBABILITY,
        min_building_size=BUILDING_MIN_SIZE,
        max_building_size=BUILDING_MAX_SIZE
    )

    visualize_map(world_map)


def sysCall_cleanup():
    """Clean up generated objects when the script stops."""

    clear_generated_objects()