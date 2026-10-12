import numpy as np
import pytest

from dcs_world.geometry.pose import Pose
from dcs_world.robot.robot import Robot
from dcs_world.robot.robot_utils import RobotConfig, RobotStatus


class ConcreteRobot(Robot):
    """Concrete implementation for testing the Robot class."""

    pass


@pytest.fixture
def config() -> RobotConfig:
    """Provide a valid robot configuration."""
    return RobotConfig(
        id="robot_01",
        max_speed=2.0,
        max_accel=1.0,
    )


@pytest.fixture
def robot(config: RobotConfig) -> ConcreteRobot:
    """Provide a robot with its default initial state."""
    return ConcreteRobot(config=config)


# ------------------------------------------------------------------
# Initialization
# ------------------------------------------------------------------


def test_robot_initialization(robot: ConcreteRobot) -> None:
    """Test initialization with default state values."""
    assert robot.pose.x == 0.0
    assert robot.pose.y == 0.0
    assert robot.pose.yaw == 0.0
    assert robot.charge == 100.0
    assert robot.status == RobotStatus.IDLE


def test_robot_initialization_with_custom_values(
    config: RobotConfig,
) -> None:
    """Test initialization with custom state values."""
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
    assert robot.status == RobotStatus.IDLE
    assert robot.config is config


# ------------------------------------------------------------------
# Constructor input validation
# ------------------------------------------------------------------


@pytest.mark.parametrize(
    "parameter, value",
    [
        ("init_x", True),
        ("init_x", "1.0"),
        ("init_x", None),
        ("init_y", False),
        ("init_y", "2.0"),
        ("init_yaw", None),
        ("init_charge", True),
        ("init_charge", "50"),
    ],
)
def test_robot_rejects_invalid_numeric_types(
    config: RobotConfig,
    parameter: str,
    value: object,
) -> None:
    """Test that numeric parameters reject invalid types."""
    with pytest.raises(TypeError):
        ConcreteRobot(**{parameter: value}, config=config)


@pytest.mark.parametrize(
    "parameter, value",
    [
        ("init_x", float("nan")),
        ("init_x", float("inf")),
        ("init_y", float("-inf")),
        ("init_yaw", float("nan")),
        ("init_charge", float("nan")),
        ("init_charge", float("inf")),
    ],
)
def test_robot_rejects_non_finite_numeric_values(
    config: RobotConfig,
    parameter: str,
    value: float,
) -> None:
    """Test that numeric parameters reject NaN and infinity."""
    with pytest.raises(ValueError):
        ConcreteRobot(**{parameter: value}, config=config)


@pytest.mark.parametrize(
    "charge",
    [-1.0, 100.1],
)
def test_robot_rejects_charge_out_of_range(
    config: RobotConfig,
    charge: float,
) -> None:
    """Test that initial charge must be between 0 and 100."""
    with pytest.raises(ValueError, match="between 0 and 100"):
        ConcreteRobot(init_charge=charge, config=config)


@pytest.mark.parametrize(
    "charge",
    [0.0, 50.0, 100.0],
)
def test_robot_accepts_valid_charge_boundaries(
    config: RobotConfig,
    charge: float,
) -> None:
    """Test valid initial battery charge values."""
    robot = ConcreteRobot(init_charge=charge, config=config)

    assert robot.charge == charge


def test_robot_requires_configuration() -> None:
    """Test that configuration must be provided."""
    with pytest.raises(ValueError, match="configuration must be provided"):
        ConcreteRobot()


def test_robot_rejects_invalid_configuration() -> None:
    """Test that configuration must be a RobotConfig instance."""
    with pytest.raises(TypeError, match="RobotConfig"):
        ConcreteRobot(config="invalid")


# ------------------------------------------------------------------
# Pose property
# ------------------------------------------------------------------


def test_robot_pose_returns_pose_instance(
    robot: ConcreteRobot,
) -> None:
    """Test that the pose property returns a Pose instance."""
    assert isinstance(robot.pose, Pose)


def test_robot_pose_returns_copy(
    robot: ConcreteRobot,
) -> None:
    """Test that modifying the returned pose does not affect robot state."""
    pose = robot.pose

    pose.x = 100.0
    pose.y = 200.0
    pose.yaw = 1.5

    assert robot.pose.x == 0.0
    assert robot.pose.y == 0.0
    assert robot.pose.yaw == 0.0


def test_robot_pose_returns_independent_instances(
    robot: ConcreteRobot,
) -> None:
    """Test that separate pose accesses return independent objects."""
    pose_1 = robot.pose
    pose_2 = robot.pose

    assert pose_1 is not pose_2
    assert pose_1 == pose_2


# ------------------------------------------------------------------
# Telemetry
# ------------------------------------------------------------------


def test_robot_telemetry(robot: ConcreteRobot) -> None:
    """Test that telemetry contains the current robot state."""
    telemetry = robot.telemetry

    assert set(telemetry.keys()) == {"pose", "charge", "status"}
    assert isinstance(telemetry["pose"], Pose)
    assert telemetry["pose"] == robot.pose
    assert telemetry["charge"] == 100.0
    assert telemetry["status"] == RobotStatus.IDLE


def test_robot_telemetry_returns_pose_copy(
    robot: ConcreteRobot,
) -> None:
    """Test that telemetry does not expose the internal pose."""
    telemetry = robot.telemetry
    telemetry["pose"].x = 100.0

    assert robot.pose.x == 0.0


# ------------------------------------------------------------------
# Movement
# ------------------------------------------------------------------


def test_robot_move_updates_pose(
    robot: ConcreteRobot,
) -> None:
    """Test that a velocity command updates the robot's pose."""
    cmd_vel = np.array([1.0, 0.5, 0.2])

    robot.move(cmd_vel, 1.0)

    assert robot.pose.x == pytest.approx(1.0)
    assert robot.pose.y == pytest.approx(0.5)
    assert robot.pose.yaw == pytest.approx(0.2)


def test_robot_move_with_different_time_step(
    robot: ConcreteRobot,
) -> None:
    """Test that the pose update scales with the time step."""
    cmd_vel = np.array([2.0, 1.0, 0.5])

    robot.move(cmd_vel, 0.5)

    assert robot.pose.x == pytest.approx(1.0)
    assert robot.pose.y == pytest.approx(0.5)
    assert robot.pose.yaw == pytest.approx(0.25)


def test_robot_move_with_zero_velocity(
    robot: ConcreteRobot,
) -> None:
    """Test that zero velocity leaves the pose unchanged."""
    initial_pose = robot.pose

    robot.move(np.zeros(3), 1.0)

    assert robot.pose.x == pytest.approx(initial_pose.x)
    assert robot.pose.y == pytest.approx(initial_pose.y)
    assert robot.pose.yaw == pytest.approx(initial_pose.yaw)


def test_robot_move_rejects_non_array_command(
    robot: ConcreteRobot,
) -> None:
    """Test that cmd_vel must be a NumPy array."""
    with pytest.raises(TypeError, match="NumPy ndarray"):
        robot.move([1.0, 0.0, 0.0], 1.0)


@pytest.mark.parametrize(
    "cmd_vel",
    [
        np.array([1.0, 0.0]),
        np.array([1.0, 0.0, 0.0, 0.0]),
        np.array([[1.0, 0.0, 0.0]]),
        np.array([]),
    ],
)
def test_robot_move_rejects_invalid_command_shape(
    robot: ConcreteRobot,
    cmd_vel: np.ndarray,
) -> None:
    """Test that cmd_vel must have shape (3,)."""
    with pytest.raises(ValueError, match="exactly 3 elements"):
        robot.move(cmd_vel, 1.0)


@pytest.mark.parametrize(
    "dt",
    [
        True,
        False,
        "1.0",
        None,
    ],
)
def test_robot_move_rejects_invalid_time_step_type(
    robot: ConcreteRobot,
    dt: object,
) -> None:
    """Test that dt must be a numeric value, excluding booleans."""
    with pytest.raises(TypeError, match="numeric value"):
        robot.move(np.zeros(3), dt)


@pytest.mark.parametrize(
    "dt",
    [
        0.0,
        -1.0,
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_robot_move_rejects_invalid_time_step_value(
    robot: ConcreteRobot,
    dt: float,
) -> None:
    """Test that dt must be finite and positive."""
    with pytest.raises(ValueError, match="finite and positive"):
        robot.move(np.zeros(3), dt)