import sys
import tty
import termios
import select
import time

from dcs_world.communication import Publisher
from dcs_world.communication.messages import (
    RobotDeploymentMessage,
    RobotStorageMessage
)


# ============================================================
# CONFIGURATION
# ============================================================

NUM_DRONES = 5

DEPLOY_TOPIC = "base.deploy"
STORE_TOPIC = "base.store"

STARTUP_DELAY = 1.0


# ============================================================
# KEYBOARD INPUT
# ============================================================

def get_key():
    """Read a single key without waiting for Enter."""

    if not select.select([sys.stdin], [], [], 0.1)[0]:
        return None

    return sys.stdin.read(1)


# ============================================================
# MAIN
# ============================================================

def main():

    deploy_publisher = Publisher(topic=DEPLOY_TOPIC)
    store_publisher = Publisher(topic=STORE_TOPIC)

    old_settings = termios.tcgetattr(sys.stdin)

    drone_states = {
        f"drone_{i}": "stored"
        for i in range(1, NUM_DRONES + 1)
    }

    print("=" * 50)
    print("DRONE DEPLOYMENT AND STORAGE TEST")
    print("=" * 50)
    print("SPACE    : Deploy next stored drone")
    print("BACKSPACE: Store next deployed drone")
    print("Q        : Quit")
    print("=" * 50)

    try:

        tty.setcbreak(sys.stdin.fileno())

        time.sleep(STARTUP_DELAY)

        while True:

            key = get_key()

            if key is None:
                continue

            if key.lower() == "q":
                break

            # ------------------------------------------------
            # DEPLOY DRONE
            # ------------------------------------------------

            if key == " ":

                id = next(
                    (
                        id
                        for id, state in drone_states.items()
                        if state == "stored"
                    ),
                    None
                )

                if id is None:
                    print("\n[TEST] No stored drones available.")
                    continue

                deploy_publisher.publish(
                    RobotDeploymentMessage(
                        id=id
                    )
                )

                drone_states[id] = "deployed"

                print(f"\n[TEST] Deployment request sent: {id}")

            # ------------------------------------------------
            # STORE DRONE
            # ------------------------------------------------

            elif key == "\x7f":

                id = next(
                    (
                        id
                        for id, state in drone_states.items()
                        if state == "deployed"
                    ),
                    None
                )

                if id is None:
                    print("\n[TEST] No deployed drones available.")
                    continue

                store_publisher.publish(
                    RobotStorageMessage(
                        id=id
                    )
                )

                drone_states[id] = "stored"

                print(f"\n[TEST] Storage request sent: {id}")

            time.sleep(0.2)

    finally:

        termios.tcsetattr(
            sys.stdin,
            termios.TCSADRAIN,
            old_settings
        )

        deploy_publisher.close()
        store_publisher.close()

        print("\n[TEST] Test terminated.")


if __name__ == "__main__":
    main()