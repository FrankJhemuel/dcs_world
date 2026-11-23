import math

from dcs_world.geometry.pose import Pose
from dcs_world.robot.drone import Drone, DroneState


# ============================================================
# CONFIGURATION
# ============================================================

DT = 0.05
MAX_STEPS = 10_000
PRINT_EVERY = 10

INITIAL_POSITION = (0.0, 0.0, 1.0)
INITIAL_YAW = 0.0

# Exploration waypoints: (x, y, z, yaw)
WAYPOINTS = [
    (3.0, 0.0, 1.0, 0.0),
    (3.0, 3.0, 1.0, math.pi / 2),
    (0.0, 3.0, 1.0, math.pi),
    (0.0, 0.0, 1.0, -math.pi / 2),
]


# ============================================================
# HELPERS
# ============================================================

def make_pose(x: float, y: float, z: float, yaw: float) -> Pose:
    """Create a Pose from position and yaw."""
    
    return Pose.from_coordinates(x, y, z, yaw)


def print_drone_status(drone: Drone, step: int) -> None:
    pose = drone.pose

    print(
        f"Step: {step:5d} | "
        f"State: {drone.state.name:10s} | "
        f"Position: "
        f"({pose.position.x:6.2f}, "
        f"{pose.position.y:6.2f}, "
        f"{pose.position.z:5.2f}) | "
        f"Yaw: {pose.yaw:6.2f} | "
        f"Target: {drone.current_target} | "
        f"Remaining: {drone.remaining_targets}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # 1. Initialize drone
    # --------------------------------------------------------

    initial_pose = make_pose(
        *INITIAL_POSITION,
        INITIAL_YAW,
    )

    drone = Drone(
        id="drone_1",
        init_pose=initial_pose,
    )

    print("\n========================================")
    print(" DRONE EXPLORATION TEST")
    print("========================================")

    print(f"Drone ID: {drone.id}")
    print(f"Initial pose: {drone.pose}")

    # --------------------------------------------------------
    # 2. Assign exploration targets
    # --------------------------------------------------------

    targets = [
        make_pose(x, y, z, yaw)
        for x, y, z, yaw in WAYPOINTS
    ]

    drone.assign_exploration(targets)

    print(f"\nAssigned {len(targets)} exploration targets.")

    # --------------------------------------------------------
    # 3. Execute manually
    # --------------------------------------------------------

    print("\nStarting exploration...\n")

    step = 0

    while drone.state != DroneState.IDLE and step < MAX_STEPS:

        drone.run(DT)

        step += 1

        if step % PRINT_EVERY == 0:
            print_drone_status(drone, step)

    # --------------------------------------------------------
    # 4. Results
    # --------------------------------------------------------

    print("\n========================================")
    print(" EXPLORATION RESULTS")
    print("========================================")

    print(f"Total steps: {step}")
    print(f"Simulated time: {step * DT:.2f} seconds")
    print(f"Final state: {drone.state.name}")
    print(f"Final pose: {drone.pose}")

    if drone.state == DroneState.IDLE:
        print("\nExploration completed successfully!")
    else:
        print("\nExploration did not finish within the step limit.")

    print("========================================\n")


if __name__ == "__main__":
    main()