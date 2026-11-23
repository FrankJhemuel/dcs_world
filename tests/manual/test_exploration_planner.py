from types import SimpleNamespace

from dcs_world.system import MissionControl
from dcs_world.geometry import Position, Pose


# ============================================================
# CONFIGURATION
# ============================================================

DRONE_IDS = [
    "drone_1",
    "drone_2",
    "drone_3",
    "drone_4",
]

EXPLORATION_AREA = (1.0, 4.0, 1.0, 4.0)

DRONE_ALTITUDE = 2.0


# ============================================================
# INITIALIZATION
# ============================================================

def initialize_mission_control():

    mission_control = MissionControl()

    # Generate map.
    mission_control.generate_map()

    # Register temporary drone models.
    # SimpleNamespace is sufficient for testing the planner.
    for drone_id in DRONE_IDS:

        drone = SimpleNamespace(
            id=drone_id,
            pose=Pose.from_coordinates(
                x=0.0,
                y=0.0,
                z=DRONE_ALTITUDE,
            ),
        )

        mission_control.drones[drone_id] = drone

    return mission_control


# ============================================================
# EXPLORATION PLANNING
# ============================================================

def test_exploration_planner():

    mission_control = initialize_mission_control()

    print("\n========================================")
    print(" EXPLORATION PLANNER TEST")
    print("========================================")

    print(f"\nExploration area: {EXPLORATION_AREA}")
    print(f"Selected drones: {DRONE_IDS}")

    # Generate exploration assignments.
    assignments = mission_control.plan_exploration_mission(
        drone_ids=DRONE_IDS,
        exploration_area=EXPLORATION_AREA,
    )

    # Display assignments.
    print("\n----------------------------------------")
    print(" EXPLORATION ASSIGNMENTS")
    print("----------------------------------------")

    for drone_id, waypoints in assignments.items():

        print(f"\n{drone_id}: {len(waypoints)} waypoints")

        for i, waypoint in enumerate(waypoints):
            position = waypoint.position

            print(
                f"  [{i + 1}] "
                f"x={position.x:.2f}, "
                f"y={position.y:.2f}, "
                f"z={position.z:.2f}"
            )

    # ========================================================
    # VALIDATION
    # ========================================================

    assigned_points = []

    for waypoints in assignments.values():
        for waypoint in waypoints:
            position = waypoint.position

            assigned_points.append(
                (position.x, position.y)
            )

            assert position.z == DRONE_ALTITUDE

    # Find all intersections inside the requested area.
    x_min, x_max, y_min, y_max = EXPLORATION_AREA

    expected_points = [
        (point.x, point.y)
        for point in mission_control.map.road_network.get_intersections()
        if (
            x_min <= point.x <= x_max
            and y_min <= point.y <= y_max
        )
    ]

    # Every intersection should be assigned exactly once.
    assert len(assigned_points) == len(set(assigned_points))
    assert set(assigned_points) == set(expected_points)

    # Every selected drone should have an assignment.
    assert set(assignments.keys()) == set(DRONE_IDS)

    print("\n----------------------------------------")
    print(" VALIDATION")
    print("----------------------------------------")

    print(f"Expected intersections: {len(expected_points)}")
    print(f"Assigned waypoints:     {len(assigned_points)}")
    print(f"Unique waypoints:       {len(set(assigned_points))}")

    print("\nAll validation checks passed!")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    test_exploration_planner()
