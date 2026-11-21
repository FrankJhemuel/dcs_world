import logging

from dcs_world.world.map import Map, MapConfig


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# MAP SNAPSHOT
# ============================================================

def get_map_snapshot(world_map: Map) -> dict:
    """Extract map data for deterministic comparison."""

    return {
        "buildings": [
            (
                building.position.x,
                building.position.y,
            )
            for building in world_map.buildings
        ],
        "obstacles": [
            (
                obstacle.x,
                obstacle.y,
            )
            for obstacle in world_map.obstacles
        ],
        "intersections": [
            (
                position.x,
                position.y,
            )
            for position in world_map.road_network.get_intersections()
        ],
        "connections": sorted({
            tuple(sorted([
                (intersection.x, intersection.y),
                (neighbor.x, neighbor.y),
            ]))
            for intersection, neighbors in world_map.road_network.roads.items()
            for neighbor in neighbors
        }),
    }

# ============================================================
# TESTS
# ============================================================


def test_same_seed():
    logger.info("Testing map generation with identical seeds...")

    config = MapConfig(seed=42)

    map_a = Map(config)
    map_b = Map(config)

    map_a.generate_map()
    map_b.generate_map()

    snapshot_a = get_map_snapshot(map_a)
    snapshot_b = get_map_snapshot(map_b)

    if snapshot_a == snapshot_b:
        logger.info("PASS: Maps generated with the same seed are identical.")
    else:
        logger.error("FAIL: Maps generated with the same seed differ.")

    logger.info(
        "Map A: %d buildings, %d obstacles, %d intersections, %d roads",
        len(map_a.buildings),
        len(map_a.obstacles),
        len(snapshot_a["intersections"]),
        len(snapshot_a["connections"]),
    )

    logger.info(
        "Map B: %d buildings, %d obstacles, %d intersections, %d roads",
        len(map_b.buildings),
        len(map_b.obstacles),
        len(snapshot_b["intersections"]),
        len(snapshot_b["connections"]),
    )

    return snapshot_a == snapshot_b


def test_different_seeds():
    logger.info("Testing map generation with different seeds...")

    map_a = Map(MapConfig(seed=42))
    map_b = Map(MapConfig(seed=123))

    map_a.generate_map()
    map_b.generate_map()

    snapshot_a = get_map_snapshot(map_a)
    snapshot_b = get_map_snapshot(map_b)

    if snapshot_a != snapshot_b:
        logger.info("PASS: Different seeds produce different maps.")
    else:
        logger.error("FAIL: Different seeds produced identical maps.")

    return snapshot_a != snapshot_b


def test_regeneration():
    logger.info("Testing map regeneration...")

    world_map = Map(MapConfig(seed=42))

    world_map.generate_map()
    first_snapshot = get_map_snapshot(world_map)

    world_map.generate_map()
    second_snapshot = get_map_snapshot(world_map)

    if first_snapshot == second_snapshot:
        logger.info("PASS: Regeneration produces the same map.")
    else:
        logger.error("FAIL: Regeneration produced a different map.")

    return first_snapshot == second_snapshot


# ============================================================
# MAIN
# ============================================================

def main():
    logger.info("=" * 55)
    logger.info("MAP GENERATION TEST SUITE")
    logger.info("=" * 55)

    results = {
        "Same seed": test_same_seed(),
        "Different seeds": test_different_seeds(),
        "Regeneration": test_regeneration(),
    }

    logger.info("=" * 55)
    logger.info("TEST SUMMARY")
    logger.info("=" * 55)

    for name, passed in results.items():
        logger.info("%-20s %s", name, "PASS" if passed else "FAIL")

    passed_count = sum(results.values())

    logger.info("-" * 55)
    logger.info("%d/%d tests passed.", passed_count, len(results))

    if not all(results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
