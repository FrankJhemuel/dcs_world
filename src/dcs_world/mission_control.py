import json
import time

from dcs_world.system import MissionControl
from dcs_world.system.model.robot_model import RobotModel

from dcs_world.communication.subscriber import Subscriber
from dcs_world.communication.messages import RobotStatusMessage


# === CONFIGURATION ===

MISSION_CONTROL_FREQUENCY = 5.0  # Hz

mission_control = MissionControl()


def on_drone_status(msg: RobotStatusMessage):
    """Process incoming drone status messages."""

    drone = mission_control.get_drone(msg.id)

    if drone is None:
        drone = RobotModel.from_status_message(msg)
        mission_control.add_drone(drone)

        print(f"[MissionControl] Registered drone: {drone.id}")

    else:
        mission_control.update_robot(
            drone.id,
            RobotModel.from_status_message(msg)
        )


def initialize_subscribers() -> list[Subscriber]:

    drone_subscriber = Subscriber(
        topic="drone_1.status",
        message_type=RobotStatusMessage,
        callback=on_drone_status
    )

    print("[MissionControl] Communication initialized.")

    return [drone_subscriber]


def main():

    subscribers = []

    try:
        subscribers = initialize_subscribers()

        period = 1.0 / MISSION_CONTROL_FREQUENCY

        print("[MissionControl] Connected and initialized.")

        while True:

            loop_start = time.perf_counter()

            for subscriber in subscribers:
                subscriber.receive()

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
        for subscriber in subscribers:
            subscriber.close()


if __name__ == "__main__":
    main()