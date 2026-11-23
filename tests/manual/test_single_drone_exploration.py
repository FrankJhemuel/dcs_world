import time
import uuid

from dcs_world.communication import Publisher, Subscriber
from dcs_world.communication.messages import (
    RobotActivationMessage,
    RobotStatusMessage,
    ExplorationTaskMessage,
    ExplorationResponseMessage,
    ExplorationResponseStatus,
)
from dcs_world.geometry import Pose


# ============================================================
# CONFIGURATION
# ============================================================

DRONE_ID = "drone_1"

POLL_INTERVAL = 0.05
STATUS_PRINT_INTERVAL = 1.0

RESPONSE_TIMEOUT = 10.0
TASK_TIMEOUT = 120.0

TARGETS = [
    Pose.from_coordinates(x=3.0, y=0.0, z=1.0, yaw=0.0),
    Pose.from_coordinates(x=3.0, y=3.0, z=1.0, yaw=1.57),
    Pose.from_coordinates(x=0.0, y=3.0, z=1.0, yaw=3.14),
    Pose.from_coordinates(x=0.0, y=0.0, z=1.0, yaw=-1.57),
]


# ============================================================
# STATE
# ============================================================

exploration_response = None

last_status_print = 0.0

subscribers = []
publishers = []


# ============================================================
# CALLBACKS
# ============================================================

def on_exploration_response(msg: ExplorationResponseMessage):
    global exploration_response

    exploration_response = msg

    print("\n[Mission Control] Exploration response received.")
    print(f"  Task ID:  {msg.task_id}")
    print(f"  Drone ID: {msg.drone_id}")
    print(f"  Status:   {msg.status.name}")
    print(f"  Reason:   {msg.reason}")


def on_drone_status(msg: RobotStatusMessage):
    global last_status_print

    current_time = time.monotonic()

    if current_time - last_status_print < STATUS_PRINT_INTERVAL:
        return

    last_status_print = current_time

    print(
        f"[Status] {msg.id} | "
        f"Position: "
        f"({msg.pose.x:.2f}, {msg.pose.y:.2f}, {msg.pose.z:.2f}) | "
        f"SOC: {msg.soc:.1f}%"
    )


# ============================================================
# COMMUNICATION
# ============================================================

def initialize_pubsub():

    # Subscribers
    response_sub = Subscriber(
        topic=f"{DRONE_ID}.explore.response",
        message_type=ExplorationResponseMessage,
        callback=on_exploration_response,
    )

    status_sub = Subscriber(
        topic=f"{DRONE_ID}.status",
        message_type=RobotStatusMessage,
        callback=on_drone_status,
    )

    subscribers.extend([
        response_sub,
        status_sub,
    ])

    # Publishers
    activation_pub = Publisher(
        topic=f"{DRONE_ID}.activate",
        handshake=True,
    )

    exploration_pub = Publisher(
        topic=f"{DRONE_ID}.explore.request",
        handshake=True,
    )

    publishers.extend([
        activation_pub,
        exploration_pub,
    ])

    return activation_pub, exploration_pub


def receive_messages():
    for subscriber in subscribers:
        subscriber.receive()


def cleanup_pubsub():

    for endpoint in subscribers + publishers:
        endpoint.close()

    subscribers.clear()
    publishers.clear()


# ============================================================
# EXPLORATION TEST
# ============================================================

def test_exploration_assignment():

    global exploration_response

    exploration_response = None

    activation_pub, exploration_pub = initialize_pubsub()

    try:

        # ----------------------------------------------------
        # Activate drone
        # ----------------------------------------------------

        print(f"\n[Mission Control] Activating {DRONE_ID}...")

        activation_pub.publish(
            RobotActivationMessage(id=DRONE_ID)
        )

        time.sleep(0.5)
        receive_messages()

        # ----------------------------------------------------
        # Create exploration task
        # ----------------------------------------------------

        task_id = str(uuid.uuid4())

        task = ExplorationTaskMessage(
            task_id=task_id,
            targets=TARGETS,
        )

        print("\n[Mission Control] Assigning exploration task.")
        print(f"  Task ID: {task_id}")
        print(f"  Number of targets: {len(TARGETS)}")

        for index, target in enumerate(TARGETS):
            print(
                f"  Target {index + 1}: "
                f"({target.x:.2f}, {target.y:.2f}, {target.z:.2f})"
            )

        exploration_pub.publish(task)

        # ----------------------------------------------------
        # Wait for task acceptance
        # ----------------------------------------------------

        print("\n[Mission Control] Waiting for response...")

        start_time = time.monotonic()

        while exploration_response is None:

            receive_messages()

            if time.monotonic() - start_time > RESPONSE_TIMEOUT:
                raise TimeoutError(
                    "Drone did not respond to the exploration request."
                )

            time.sleep(POLL_INTERVAL)

        # ----------------------------------------------------
        # Verify initial response
        # ----------------------------------------------------

        response = exploration_response

        assert response.task_id == task_id
        assert response.drone_id == DRONE_ID

        if response.status != ExplorationResponseStatus.ACCEPTED:
            raise RuntimeError(
                f"Task rejected: {response.reason}"
            )

        print("\n[Mission Control] Exploration task accepted!")

        # ----------------------------------------------------
        # Monitor task execution
        # ----------------------------------------------------

        print("\n[Mission Control] Monitoring exploration...\n")

        exploration_response = None
        start_time = time.monotonic()

        while True:

            receive_messages()

            if exploration_response is not None:

                response = exploration_response

                if response.task_id != task_id:
                    exploration_response = None
                    continue

                if response.status == ExplorationResponseStatus.COMPLETED:
                    print("\n[Mission Control] Exploration completed successfully!")
                    break

                if response.status == ExplorationResponseStatus.FAILED:
                    raise RuntimeError(
                        f"Exploration failed: {response.reason}"
                    )

                exploration_response = None

            if time.monotonic() - start_time > TASK_TIMEOUT:
                raise TimeoutError(
                    "Exploration task did not finish within the allowed time."
                )

            time.sleep(POLL_INTERVAL)

    finally:
        cleanup_pubsub()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:
        test_exploration_assignment()

    except KeyboardInterrupt:
        print("\n[Mission Control] Test interrupted.")

    except Exception as error:
        print(f"\n[Mission Control] Test failed: {error}")

    finally:
        cleanup_pubsub()
        print("[Mission Control] Test finished.")