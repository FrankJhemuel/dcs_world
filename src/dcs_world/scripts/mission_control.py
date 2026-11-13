import time

from dcs_world.system import MissionControl
from dcs_world.system.coppelia_client import CoppeliaClient
from dcs_world.robot import Drone, GroundRobot

from dcs_world.system.model.robot_model import RobotModel

from dcs_world.communication.subscriber import Subscriber
from dcs_world.communication.messages import RobotStatusMessage


# === CONFIGURATION ===

MISSION_CONTROL_FREQUENCY = 10.0  # Hz


def on_drone_status(
    mission_control: MissionControl,
    msg: RobotStatusMessage
):
    """Process incoming drone status messages."""

    drone = mission_control.get_drone(msg.id)

    if drone is None:
    
        # === INITIALIZE DRONE ===

        drone = RobotModel.from_status_message(msg)

        mission_control.add_drone(drone)
        print(f"[MissionControl] Registered drone: {drone.id}")




def initialize_mission_control(
    coppelia: CoppeliaClient
) -> tuple[MissionControl, list[Subscriber]]:
    """Initialize mission control and register its elements."""

    mission_control = MissionControl()


    # === INITIALIZE COMMUNICATION ===

    drone_subscriber = Subscriber(
        sim=coppelia.sim,
        topic="dcs_world.drone_1.status",
        message_type=RobotStatusMessage,
        callback=lambda msg: on_drone_status(mission_control, msg)
    )

    subscribers = [
        drone_subscriber
    ]

    print("[MissionControl] Communication initialized.")

    return mission_control, subscribers


def main():

    # Initialize CoppeliaSim connection
    coppelia = CoppeliaClient()

    try:

        # Initialize mission control
        mission_control, subscribers = initialize_mission_control(coppelia)

        period = 1.0 / MISSION_CONTROL_FREQUENCY

        print("[MissionControl] Connected and initialized.")

        # === EXECUTION LOOP ===

        while True:

            loop_start = time.perf_counter()

            # Receive incoming messages
            for subscriber in subscribers:
                subscriber.receive()

            # Mission control execution
            # mission_control.update()

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