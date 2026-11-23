import time
import uuid
import threading
import queue

from dcs_world.robot.utils.robot_status import RobotStatus
from dcs_world.system import MissionControl
from dcs_world.system.model.robot_model import RobotModel
from dcs_world.system.model.robot_model import DeploymentState

from dcs_world.communication import Subscriber, Publisher

from dcs_world.communication.messages import (
    RobotStatusMessage,
    RobotDeploymentMessage,
    RobotStorageMessage,
    RobotManagementResponseMessage,
    ExplorationTaskMessage,
    ExplorationResponseMessage,
)

from dcs_world.geometry import Pose

#* ============================================================
#* CONFIGURATION
#* ============================================================

MISSION_CONTROL_FREQUENCY = 5.0  # Hz

DEPLOYMENT_STAGGER_DELAY = 3.0  # seconds
DEPLOYMENT_TIMEOUT = 30.0       # seconds

DEPLOY_TOPIC = "base.deploy"
STORE_TOPIC = "base.store"

DEPLOY_RESPONSE_TOPIC = "base.deploy.response"
STORE_RESPONSE_TOPIC = "base.store.response"

ROBOT_STATUS_TOPIC = "*.status"
EXPLORATION_RESPONSE_TOPIC = "drone_*.explore.response"

SEED = 42

#* ============================================================
#* GLOBAL VARIABLES
#* ============================================================

mission_control = None

subscribers = []
publishers = []

exploration_publishers = {}

command_queue = queue.Queue()


#* ============================================================
#* CALLBACKS
#* ============================================================

# Robot callbacks

def on_robot_status(msg: RobotStatusMessage):
    """Process incoming robot status messages."""

    robot = RobotModel.from_status_message(msg)

    existing_robot = mission_control.all_robots.get(robot.id)

    if existing_robot is None:

        if robot.robot_type == "Drone":
            mission_control.add_drone(robot)

        elif robot.robot_type == "GroundRobot":
            mission_control.add_ground_robot(robot)

        print(
            f"[MissionControl] Registered robot: {robot.id}"
        )

    else:
        mission_control.update_robot(robot.id, robot)

# Deployment callbacks

def on_deployment_response(msg: RobotManagementResponseMessage):
    """Process deployment responses received from the base."""

    print(
        f"\n[MissionControl] Deployment response | "
        f"Robot: {msg.id} | "
        f"Status: {msg.status.name}"
    )

    if msg.reason:
        print(f"[MissionControl] Reason: {msg.reason}")

# Storage callbacks

def on_storage_response(msg: RobotManagementResponseMessage):
    """Process storage responses received from the base."""

    print(
        f"\n[MissionControl] Storage response | "
        f"Robot: {msg.id} | "
        f"Status: {msg.status.name}"
    )

    if msg.reason:
        print(f"[MissionControl] Reason: {msg.reason}")

# Exploration callbacks

def on_exploration_response(msg: ExplorationResponseMessage):
    """Process exploration task responses received from a drone."""

    print(
        f"\n[MissionControl] Exploration response | "
        f"Task: {msg.task_id} | "
        f"Drone: {msg.id} | "
        f"Status: {msg.status.name}"
    )

    if msg.reason:
        print(f"[MissionControl] Reason: {msg.reason}")

#* ============================================================
#* COMMUNICATION
#* ============================================================

# Endpoint initialization

def initialize_handles():
    """Initialize communication endpoint collections."""

    global subscribers, publishers

    subscribers = []
    publishers = []

    exploration_publishers.clear()

# Publisher and subscriber initialization

def initialize_pubsub():

    # --------------------------------------------------------
    # Subscribers
    # --------------------------------------------------------

    robot_status_sub = Subscriber(
        topic=ROBOT_STATUS_TOPIC,
        message_type=RobotStatusMessage,
        callback=on_robot_status,
    )

    deployment_response_sub = Subscriber(
        topic=DEPLOY_RESPONSE_TOPIC,
        message_type=RobotManagementResponseMessage,
        callback=on_deployment_response,
    )

    storage_response_sub = Subscriber(
        topic=STORE_RESPONSE_TOPIC,
        message_type=RobotManagementResponseMessage,
        callback=on_storage_response,
    )

    exploration_response_sub = Subscriber(
        topic=EXPLORATION_RESPONSE_TOPIC,
        message_type=ExplorationResponseMessage,
        callback=on_exploration_response,
    )

    # --------------------------------------------------------
    # Publishers
    # --------------------------------------------------------

    deploy_pub = Publisher(
        topic=DEPLOY_TOPIC,
    )

    store_pub = Publisher(
        topic=STORE_TOPIC,
    )

    # --------------------------------------------------------
    # Register endpoints
    # --------------------------------------------------------

    subscribers.extend([
        robot_status_sub,
        deployment_response_sub,
        storage_response_sub,
        exploration_response_sub,
    ])

    publishers.extend([
        deploy_pub,
        store_pub,
    ])

# Exploration publisher management

def get_exploration_publisher(robot_id: str) -> Publisher:
    """Get or create an exploration publisher for a drone."""

    if robot_id not in exploration_publishers:

        exploration_publishers[robot_id] = Publisher(
            topic=f"{robot_id}.explore.request",
            handshake=True,
        )

    return exploration_publishers[robot_id]

# Message reception

def receive_messages():
    """Process pending messages from all subscribers."""

    for subscriber in subscribers:
        subscriber.receive()

# Communication cleanup

def cleanup_pubsub():
    """Close all communication endpoints."""

    for endpoint in subscribers + publishers:
        endpoint.close()

    for publisher in exploration_publishers.values():
        publisher.close()

    subscribers.clear()
    publishers.clear()
    exploration_publishers.clear()

#* ============================================================
#* ROBOT MANAGEMENT
#* ============================================================

# Deployment

def request_deployment(robot_id: str):
    """Request deployment of a robot through the base."""

    message = RobotDeploymentMessage(id=robot_id)

    publishers[0].publish(message)

    print(
        f"[MissionControl] Deployment requested: {robot_id}"
    )

# Deployment confirmation

def wait_for_deployment(robot_id: str) -> bool:
    """Wait until a drone reports that it has been deployed."""

    start_time = time.perf_counter()

    while time.perf_counter() - start_time < DEPLOYMENT_TIMEOUT:

        receive_messages()

        drone = mission_control.get_drone(robot_id)

        if (
            drone is not None
            and drone.deployment_state == DeploymentState.DEPLOYED
        ):
            print(
                f"[MissionControl] {robot_id} successfully deployed."
            )
            return True

        time.sleep(0.1)

    print(
        f"[MissionControl] Deployment timeout: {robot_id}"
    )

    return False

# Sequential deployment

def deploy_drones_sequentially(drone_ids: list[str]) -> bool:
    """Deploy drones sequentially with a stagger delay."""

    if not drone_ids:
        print(
            "[MissionControl] No drones selected."
        )
        return False

    # Validate all selected drones before starting deployment.
    for drone_id in drone_ids:

        drone = mission_control.get_drone(drone_id)

        if drone is None:
            print(
                f"[MissionControl] Drone not found: {drone_id}"
            )
            return False

    # --------------------------------------------------------
    # Deploy drones one by one
    # --------------------------------------------------------

    for index, drone_id in enumerate(drone_ids):

        drone = mission_control.get_drone(drone_id)

        # Skip drones that are already deployed.
        if drone.deployment_state == DeploymentState.DEPLOYED:

            print(
                f"[MissionControl] {drone_id} is already deployed."
            )

            continue

        print(
            f"\n[MissionControl] Deploying {drone_id} "
            f"({index + 1}/{len(drone_ids)})..."
        )

        request_deployment(drone_id)

        # Wait for deployment confirmation.
        if not wait_for_deployment(drone_id):

            print(
                "[MissionControl] Deployment sequence aborted."
            )

            return False

        # Stagger the next deployment.
        if index < len(drone_ids) - 1:

            print(
                f"[MissionControl] Waiting "
                f"{DEPLOYMENT_STAGGER_DELAY:.1f}s "
                f"before deploying the next drone..."
            )

            delay_start = time.perf_counter()

            while (
                time.perf_counter() - delay_start
                < DEPLOYMENT_STAGGER_DELAY
            ):
                receive_messages()
                time.sleep(0.1)

    print(
        "\n[MissionControl] All selected drones are deployed."
    )

    return True

# Storage

def request_storage(robot_id: str):
    """Request storage of a robot through the base."""

    message = RobotStorageMessage(id=robot_id)

    publishers[1].publish(message)

    print(
        f"[MissionControl] Storage requested: {robot_id}"
    )

#* ============================================================
#* EXPLORATION MANAGEMENT
#* ============================================================

# Exploration task assignment

def assign_exploration_task(
    robot_id: str,
    targets: list[Pose],
):
    """Assign an exploration task to a drone."""

    drone = mission_control.get_drone(robot_id)

    if drone is None:
        print(
            f"[MissionControl] Drone not found: {robot_id}"
        )
        return

    task_id = uuid.uuid4().hex

    message = ExplorationTaskMessage(
        task_id=task_id,
        targets=targets,
    )

    publisher = get_exploration_publisher(robot_id)

    publisher.publish(message)

    print(
        f"[MissionControl] Exploration task assigned | "
        f"Task: {task_id} | "
        f"Drone: {robot_id} | "
        f"Targets: {len(targets)}"
    )

# Exploration mission execution

def execute_exploration_mission(drone_ids, exploration_area):
    """Stagger drone deployment and assign tasks individually."""

    try:
        assignments = mission_control.plan_exploration_mission(
            drone_ids=drone_ids,
            exploration_area=exploration_area,
        )

    except (ValueError, KeyError) as error:
        print(f"[MissionControl] Planning failed: {error}")
        return

    for index, robot_id in enumerate(drone_ids):

        drone = mission_control.get_drone(robot_id)

        if drone is None:
            print(f"[MissionControl] Unknown drone: {robot_id}")
            continue

        # ------------------------------------------------
        # DEPLOYMENT
        # ------------------------------------------------

        if drone.deployment_state != DeploymentState.DEPLOYED:

            print(
                f"\n[MissionControl] Deploying "
                f"{robot_id} ({index + 1}/{len(drone_ids)})..."
            )

            request_deployment(robot_id)

            if not wait_for_deployment(robot_id):
                print(
                    f"[MissionControl] Skipping {robot_id}: "
                    "deployment unsuccessful."
                )
                continue

        # ------------------------------------------------
        # EXPLORATION TASK ASSIGNMENT
        # ------------------------------------------------

        print(
            f"[MissionControl] Assigning exploration task "
            f"to {robot_id}..."
        )

        assign_exploration_task(
            robot_id=robot_id,
            targets=assignments[robot_id],
        )

        # ------------------------------------------------
        # STAGGERED DEPLOYMENT DELAY
        # ------------------------------------------------

        if index < len(drone_ids) - 1:

            print(
                f"[MissionControl] Waiting "
                f"{DEPLOYMENT_STAGGER_DELAY}s before next deployment..."
            )

            time.sleep(DEPLOYMENT_STAGGER_DELAY)

    print("\n[MissionControl] Exploration mission dispatched.")

#* ============================================================
#* MENU INTERFACE
#* ============================================================

# Robot information

def display_robots():
    """Display all registered robots."""

    robots = mission_control.all_robots

    print("\n========== REGISTERED ROBOTS ==========")

    if not robots:
        print("No robots registered.")
        return

    for robot in robots.values():

        print(
            f"ID: {robot.id} | "
            f"Type: {robot.robot_type} | "
            f"Status: {robot.status.name} | "
            f"Deployment: {robot.deployment_state.name} | "
            f"Task: {robot.task_status.name} | "
            f"SoC: {robot.soc:.1f}%"
        )

    print("=======================================\n")

# Manual exploration menu

def menu_assign_exploration():
    """Collect exploration task information from the user."""

    print("\n========== ASSIGN EXPLORATION ==========")

    robot_id = input("Drone ID: ").strip()

    drone = mission_control.get_drone(robot_id)

    if drone is None:
        print(
            f"[MissionControl] Drone not found: {robot_id}"
        )
        return

    try:
        x = float(input("Target X: "))
        y = float(input("Target Y: "))
        z = float(input("Target Z: "))
        yaw = float(input("Target Yaw (rad): "))

    except ValueError:
        print("[MissionControl] Invalid target coordinates.")
        return

    target = Pose.from_coordinates(
        x=x,
        y=y,
        z=z,
        yaw=yaw,
    )

    assign_exploration_task(
        robot_id=robot_id,
        targets=[target],
    )

# Exploration planning menu

def menu_plan_exploration():
    """Collect drone selection and exploration area."""

    print("\n========== PLAN EXPLORATION ==========")

    # DRONE SELECTION

    drone_ids_input = input(
        "Select drones (e.g. 1,2,3,4,5) [Enter = all available]: "
    ).strip()

    if drone_ids_input:

        try:
            drone_ids = [
                f"drone_{int(drone_id.strip())}"
                for drone_id in drone_ids_input.split(",")
                if drone_id.strip()
            ]

            if len(drone_ids) != len(set(drone_ids)):
                print("[MissionControl] Duplicate drone IDs.")
                return

        except ValueError:
            print("[MissionControl] Invalid drone selection.")
            return

    else:

        drone_ids = [
            drone.id
            for drone in mission_control.drones.values()
            if (
                drone.deployment_state == DeploymentState.STORED
                and drone.status == RobotStatus.IDLE
            )
        ]

        if not drone_ids:
            print("[MissionControl] No available drones to deploy.")
            return

        print(
            f"[MissionControl] Automatically selected "
            f"{len(drone_ids)} available drones: {drone_ids}"
        )

    if not drone_ids:
        print("[MissionControl] No drones selected.")
        return

    # EXPLORATION AREA SELECTION

    print("\nExploration area:")
    print("1. Entire map")
    print("2. Custom area")

    try:
        area_choice = input("Select area: ").strip()

        if area_choice == "1":

            exploration_area = mission_control.get_exploration_bounds()

        elif area_choice == "2":

            x_min = float(input("Area X minimum: "))
            x_max = float(input("Area X maximum: "))
            y_min = float(input("Area Y minimum: "))
            y_max = float(input("Area Y maximum: "))

            exploration_area = (
                x_min,
                x_max,
                y_min,
                y_max,
            )

        else:
            print("[MissionControl] Invalid area selection.")
            return

        print(
            f"\n[MissionControl] Selected drones: {drone_ids}"
        )
        print(
            f"[MissionControl] Exploration area: {exploration_area}"
        )

    except ValueError:
        print("[MissionControl] Invalid input.")
        return

    command_queue.put((
        "plan_exploration",
        (drone_ids, exploration_area),
    ))

# Main menu

def display_menu():
    """Display available Mission Control commands."""

    print("\n")
    print("========================================")
    print("             MISSION CONTROL")
    print("========================================")
    print("1. List registered robots")
    print("2. Assign exploration task")
    print("3. Request drone deployment")
    print("4. Request drone storage")
    print("5. Plan and assign exploration mission")
    print("0. Exit")
    print("========================================")

# Menu input

def menu_input_loop():
    """Continuously collect user commands."""

    while True:

        display_menu()

        choice = input("Select an option: ").strip()

        if choice == "0":

            command_queue.put(("exit", None))
            break

        elif choice == "1":

            command_queue.put(("list_robots", None))

        elif choice == "2":

            robot_id = input("Drone ID: ").strip()

            try:
                x = float(input("Target X: "))
                y = float(input("Target Y: "))
                z = float(input("Target Z: "))
                yaw = float(input("Target Yaw (rad): "))

                command_queue.put((
                    "exploration",
                    (robot_id, x, y, z, yaw),
                ))

            except ValueError:
                print("[MissionControl] Invalid target coordinates.")

        elif choice == "3":

            robot_id = input("Drone ID: ").strip()

            command_queue.put((
                "deployment",
                robot_id,
            ))

        elif choice == "4":

            robot_id = input("Drone ID: ").strip()

            command_queue.put((
                "storage",
                robot_id,
            ))

        elif choice == "5":

            menu_plan_exploration()

        else:

            print("[MissionControl] Invalid option.")

# Command processing

def process_commands():
    """Process commands collected by the menu interface."""

    while not command_queue.empty():

        command, args = command_queue.get()

        if command == "exit":

            return False

        elif command == "list_robots":

            display_robots()

        elif command == "exploration":

            robot_id, x, y, z, yaw = args

            target = Pose.from_coordinates(
                x=x,
                y=y,
                z=z,
                yaw=yaw,
            )

            assign_exploration_task(
                robot_id=robot_id,
                targets=[target],
            )

        elif command == "deployment":

            request_deployment(args)

        elif command == "storage":

            request_storage(args)

        elif command == "plan_exploration":

            drone_ids, exploration_area = args

            execute_exploration_mission(
                drone_ids=drone_ids,
                exploration_area=exploration_area,
            )

    return True


#* ============================================================
#* INITIALIZATION
#* ============================================================

def initialization():
    """Initialize Mission Control and communication."""

    global mission_control

    # --------------------------------------------------------
    # Mission Control initialization
    # --------------------------------------------------------

    mission_control = MissionControl()

    mission_control.generate_map(
        seed=SEED
    )

    # --------------------------------------------------------
    # Communication initialization
    # --------------------------------------------------------

    initialize_handles()
    initialize_pubsub()

    print(
        "[MissionControl] Communication initialized."
    )


#* ============================================================
#* EXECUTION
#* ============================================================

def main():

    try:

        # ----------------------------------------------------
        # Initialization
        # ----------------------------------------------------

        initialization()

        period = 1.0 / MISSION_CONTROL_FREQUENCY

        # ----------------------------------------------------
        # Start menu input thread
        # ----------------------------------------------------

        menu_thread = threading.Thread(
            target=menu_input_loop,
            daemon=True,
        )

        menu_thread.start()

        print(
            "[MissionControl] Connected and initialized."
        )

        # ----------------------------------------------------
        # Main execution loop
        # ----------------------------------------------------

        running = True

        while running:

            loop_start = time.perf_counter()

            # Receive incoming messages.
            receive_messages()

            # Process user commands.
            running = process_commands()

            # Maintain execution frequency.
            elapsed = time.perf_counter() - loop_start
            remaining = period - elapsed

            if remaining > 0:
                time.sleep(remaining)

            else:
                print(
                    f"[MissionControl] Warning: "
                    f"Execution time exceeded period by "
                    f"{-remaining:.4f} seconds."
                )

    except KeyboardInterrupt:

        print(
            "\n[MissionControl] Stopping..."
        )

    finally:

        # ----------------------------------------------------
        # Cleanup
        # ----------------------------------------------------

        cleanup_pubsub()

        print(
            "[MissionControl] Shutdown complete."
        )


#* ============================================================
#* ENTRY POINT
#* ============================================================

if __name__ == "__main__":
    main()
