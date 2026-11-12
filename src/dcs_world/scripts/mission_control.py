from dcs_world.system import MissionControl
from dcs_world.system.coppelia_client import CoppeliaClient


def main():

    # Initialize CoppeliaSim connection
    coppelia = CoppeliaClient()

    # Initialize mission control
    mission_control = MissionControl()

    # Start simulation
    coppelia.start_simulation()

    try:
        while True:
            # Mission control execution loop
            pass

    except KeyboardInterrupt:
        print("Stopping mission...")

    finally:
        coppelia.stop_simulation()


if __name__ == "__main__":
    main()