import numpy as np
import pytest

from dcs_world.geometry.pose import Pose
from dcs_world.robot.robot import Robot
from dcs_world.robot.robot_utils import RobotConfig, RobotStatus


class ConcreteRobot(Robot):
    """Concrete implementation for testing the abstract Robot class."""

    def move(self, cmd_vel: np.ndarray) -> None:
        pass


@pytest.fixture
def config() -> RobotConfig:
    return RobotConfig(
        id="robot_01",
        max_speed=2.0,
        max_accel=1.0,
    )


@pytest.fixture
def robot(config: RobotConfig) -> ConcreteRobot:
    return ConcreteRobot(config=config)


def test_robot_initialization(robot: ConcreteRobot) -> None:
    assert robot.pose.x == 0.0
    assert robot.pose.y == 0.0
    assert robot.pose.yaw == 0.0
    assert robot.charge == 100.0
    assert robot.status == RobotStatus.IDLE


def test_robot_initialization_with_custom_values(
    config: RobotConfig,
) -> None:
    robot = ConcreteRobot(
        init_x=1.5,
        init_y=2.5,
        init_yaw=0.75,
        init_charge=60.0,
        config=config,
    )

    assert robot.pose.x == 1.5
    assert robot.pose.y == 2.5
    assert robot.pose.yaw == 0.75
    assert robot.charge == 60.0


def test_robot_pose_returns_pose_copy(robot: ConcreteRobot) -> None:
    pose = robot.pose

    assert isinstance(pose, Pose)

    # Modifying the returned pose should not modify the robot's internal pose.
    pose.x = 100.0

    assert robot.pose.x == 0.0


def test_robot_telemetry(robot: ConcreteRobot) -> None:
    telemetry = robot.telemetry

    assert telemetry["pose"] == robot.pose
    assert telemetry["charge"] == 100.0
    assert telemetry["status"] == RobotStatus.IDLE


@pytest.mark.parametrize(
    "parameter,value",
    [
        ("init_x", True),
        ("init_y", "1.0"),
        ("init_yaw", None),
        ("init_charge", False),
    ],
)
def test_robot_rejects_invalid_numeric_types(
    config: RobotConfig,
    parameter: str,
    value: object,
) -> None:
    with pytest.raises(TypeError):
        ConcreteRobot(**{parameter: value}, config=config)


@pytest.mark.parametrize("charge", [-1.0, 100.1])
def test_robot_rejects_charge_out_of_range(
    config: RobotConfig,
    charge: float,
) -> None:
    with pytest.raises(ValueError, match="between 0 and 100"):
        ConcreteRobot(init_charge=charge, config=config)


@pytest.mark.parametrize("charge", [0.0, 100.0])
def test_robot_accepts_charge_boundaries(
    config: RobotConfig,
    charge: float,
) -> None:
    robot = ConcreteRobot(init_charge=charge, config=config)

    assert robot.charge == charge


def test_robot_requires_configuration() -> None:
    with pytest.raises(ValueError, match="configuration must be provided"):
        ConcreteRobot()


def test_robot_rejects_invalid_configuration() -> None:
    with pytest.raises(TypeError, match="RobotConfig"):
        ConcreteRobot(config="invalid")