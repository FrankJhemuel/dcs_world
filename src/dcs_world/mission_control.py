import json
import time

from dcs_world.system import MissionControl
from dcs_world.system.coppelia_client import CoppeliaClient

from dcs_world.system.model.robot_model import RobotModel

from dcs_world.communication.subscriber import Subscriber
from dcs_world.communication.messages import RobotStatusMessage


# === CONFIGURATION ===

MISSION_CONTROL_FREQUENCY = 5.0  # Hz

mission_control = MissionControl()

def on_drone_status(
    msg: RobotStatusMessage
):
    """Process incoming drone status messages."""

    drone = mission_control.get_drone(msg.id)

    if drone is None:
    
        # === INITIALIZE DRONE ===
        drone = RobotModel.from_status_message(msg)

        mission_control.add_drone(drone)
        print(f"[MissionControl] Registered drone: {drone.id}")
        print(json.dumps(drone.to_dict(), indent=4))
    else:
        # === UPDATE DRONE STATUS ===
        mission_control.update_robot(drone.id, RobotModel.from_status_message(msg))
        print(f"[MissionControl] Updated drone: {drone.id}")
        print(json.dumps(drone.to_dict(), indent=4))

def initialize_subscribers(
    coppelia: CoppeliaClient
) -> list[Subscriber]:
    """Initialize mission control and register its elements."""
    # === INITIALIZE COMMUNICATION ===

    drone_subscriber = Subscriber(
        sim=coppelia.sim,
        topic="drone_1.status",
        message_type=RobotStatusMessage,
        callback=lambda msg: on_drone_status(msg)
    )

    subscribers = [
        drone_subscriber
    ]

    print("[MissionControl] Communication initialized.")

    return subscribers


def main():

    # Initialize CoppeliaSim connection
    coppelia = CoppeliaClient()

    try:

        # Initialize mission control
        subscribers = initialize_subscribers(coppelia)

        period = 1.0 / MISSION_CONTROL_FREQUENCY

        print("[MissionControl] Connected and initialized.")

        # === EXECUTION LOOP ===

        while True:

            loop_start = time.perf_counter()

            # Receive incoming messages
            for subscriber in subscribers:
                subscriber.receive()

            # if mission_control.get_drone("drone_1") is not None:
            #     print(json.dumps(mission_control.get_drone("drone_1").to_dict(), indent=4))

            # Maintain execution frequency
            elapsed = time.perf_counter() - loop_start
            remaining = period - elapsed

            if remaining > 0:
                time.sleep(remaining)
            else:
                print(
                    f"[MissionControl] Warning: "
                    f"Execution time exceeded period by {-remaining:.4f} seconds."
                )

    except KeyboardInterrupt:
        print("[MissionControl] Stopping...")

    finally:
        coppelia.disconnect()


if __name__ == "__main__":
    main()