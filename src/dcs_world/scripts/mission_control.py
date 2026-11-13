import time

from dcs_world.system import MissionControl
from dcs_world.system.coppelia_client import CoppeliaClient
from dcs_world.robot import Drone, GroundRobot
from dcs_world.system.model.robot_model import RobotModel


# === CONFIGURATION ===

MISSION_CONTROL_FREQUENCY = 10.0  # Hz


def initialize_mission_control(
    coppelia: CoppeliaClient
) -> MissionControl:
    """Initialize mission control and register its elements."""

    mission_control = MissionControl()

    # === INITIALIZE DRONE ===

    drone_info = coppelia.wait_for_robot("drone_1")

    drone = RobotModel(**drone_info)

    mission_control.add_drone(drone)

    print(f"[MissionControl] Registered drone: {drone.id}")

    return mission_control


def main():

    # Initialize CoppeliaSim connection
    coppelia = CoppeliaClient()

    try:
        # Initialize mission control
        mission_control = initialize_mission_control(coppelia)

        period = 1.0 / MISSION_CONTROL_FREQUENCY

        print("[MissionControl] Connected and initialized.")

        # === EXECUTION LOOP ===

        while True:
            loop_start = time.perf_counter()

            # Mission control execution
            print(
                f"Registered robots: "
                f"{len(mission_control.all_robots)}"
            )

            # Maintain execution frequency
            elapsed = time.perf_counter() - loop_start
            remaining = period - elapsed

            if remaining > 0:
                time.sleep(remaining)

    except KeyboardInterrupt:
        print("[MissionControl] Stopping...")

    finally:
        coppelia.disconnect()


if __name__ == "__main__":
    main()