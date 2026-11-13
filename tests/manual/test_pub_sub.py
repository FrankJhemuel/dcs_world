from dcs_world.communication.messages import RobotStatusMessage
from dcs_world.communication.serializer import serialize, deserialize

from dcs_world.geometry.pose import Pose
from dcs_world.geometry.twist import Twist
from dcs_world.robot.utils.robot_status import RobotStatus
from dcs_world.system.model.robot_model import RobotModel


def message_to_model(message: RobotStatusMessage) -> RobotModel:
    """Convert a communication message into an internal robot model."""

    return RobotModel(
        id=message.id,
        robot_type=message.robot_type,
        pose=message.pose,
        velocity=message.velocity,
        soc=message.soc,
        status=message.status
    )


def main():

    # === CREATE MESSAGE ===

    original = RobotStatusMessage(
        timestamp=10.5,
        id="drone_1",
        robot_type="Drone",
        pose=Pose.from_coordinates(x=1.0, y=2.0, z=3.0, yaw=0.5),
        velocity=Twist(linear=[0.01, 0.02, 0.03], angular=[0.01, 0.02, 0.03]),
        soc=85.0,
        status=RobotStatus.EXECUTING
    )

    # === SERIALIZATION ===

    json_data = serialize(original, indent=4)

    print("\n=== SERIALIZED ===")
    print(json_data)

    # === DESERIALIZATION ===

    received = deserialize(json_data, RobotStatusMessage)

    assert received == original

    print("\n[PASS] Serialization and deserialization")

    # === MODEL CONVERSION ===

    robot = message_to_model(received)

    assert isinstance(robot, RobotModel)
    assert robot.id == original.id
    assert robot.pose == original.pose
    assert robot.velocity == original.velocity
    assert robot.status == original.status

    print("\n[PASS] RobotModel conversion")

    print("\nAll tests passed!")


if __name__ == "__main__":
    main()