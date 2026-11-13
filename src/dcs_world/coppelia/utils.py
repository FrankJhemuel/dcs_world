DRONE_ID_SIGNAL = "dcs_world.drone_id_counter"
GROUND_ROBOT_ID_SIGNAL = "dcs_world.ground_robot_id_counter"

def get_next_drone_id(sim) -> str:
    """Generate a unique drone ID using a CoppeliaSim integer signal."""

    counter = sim.getInt32Signal(DRONE_ID_SIGNAL)

    if counter is None:
        counter = 0

    counter += 1
    sim.setInt32Signal(DRONE_ID_SIGNAL, counter)

    return f"drone_{counter}"

def get_next_ground_robot_id(sim) -> str:
    """Generate a unique ground robot ID using a CoppeliaSim integer signal."""

    counter = sim.getInt32Signal(GROUND_ROBOT_ID_SIGNAL)

    if counter is None:
        counter = 0

    counter += 1
    sim.setInt32Signal(GROUND_ROBOT_ID_SIGNAL, counter)

    return f"ground_robot_{counter}"