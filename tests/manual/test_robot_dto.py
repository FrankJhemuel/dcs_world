import json

from dcs_world.geometry.vector3 import Vector3
from dcs_world.system.model.robot_model import RobotDTO
from dcs_world.robot.utils.robot_status import RobotStatus
from dcs_world.geometry.pose import Pose
from dcs_world.geometry.twist import Twist


def main():
    robot = RobotDTO(
        id=1,
        robot_type="Drone",
        pose=Pose(x=0.0, y=0.0, yaw=0.0),       # Replace with your constructor arguments
        velocity=Twist(linear=Vector3(x=0.0, y=0.0, z=0.0), angular=Vector3(x=0.0, y=0.0, z=0.0)),  # Replace with your constructor arguments
        soc=0.85,
        status=RobotStatus.FLYING
    )

    # Test dictionary conversion
    robot_dict = robot.to_dict()

    print("=== DICTIONARY ===")
    print(robot_dict)
    print(type(robot_dict))
    print(type(robot_dict["pose"]))
    print(type(robot_dict["velocity"]))

    # Test JSON conversion
    robot_json = robot.to_json()

    print("\n=== JSON ===")
    print(json.dumps(json.loads(robot_json), indent=4))

    # Verify nested dictionaries
    assert isinstance(robot_dict, dict)
    assert isinstance(robot_dict["pose"], dict)
    assert isinstance(robot_dict["velocity"], dict)
    assert robot_dict["status"] == "FLYING"

    print("\nAll tests passed!")


if __name__ == "__main__":
    main()