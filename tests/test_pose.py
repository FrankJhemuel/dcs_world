import numpy as np
import pytest

from dcs_world.geometry.pose import Pose


# ------------------------------------------------------------------
# Initialization
# ------------------------------------------------------------------


def test_pose_initialization() -> None:
    """Test initialization with position and orientation."""
    pose = Pose(x=1.0, y=2.0, yaw=0.5)

    assert pose.x == 1.0
    assert pose.y == 2.0
    assert pose.yaw == 0.5


# ------------------------------------------------------------------
# NumPy array conversion
# ------------------------------------------------------------------


def test_pose_as_np_array() -> None:
    """Test conversion of the pose to a NumPy array."""
    pose = Pose(x=1.0, y=2.0, yaw=0.5)

    np.testing.assert_array_equal(
        pose.as_np_array,
        np.array([1.0, 2.0, 0.5]),
    )


def test_pose_as_np_array_returns_independent_array() -> None:
    """Test that modifying the returned array does not change the pose."""
    pose = Pose(x=1.0, y=2.0, yaw=0.5)

    array = pose.as_np_array
    array[0] = 100.0

    assert pose.x == 1.0
    assert pose.y == 2.0
    assert pose.yaw == 0.5


# ------------------------------------------------------------------
# NumPy array setter
# ------------------------------------------------------------------


def test_pose_as_np_array_setter() -> None:
    """Test updating the pose from a NumPy array."""
    pose = Pose(x=0.0, y=0.0, yaw=0.0)

    pose.as_np_array = np.array([1.5, 2.5, 1.0])

    assert pose.x == 1.5
    assert pose.y == 2.5
    assert pose.yaw == 1.0


def test_pose_setter_rejects_non_numpy_array() -> None:
    """Test that the setter requires a NumPy ndarray."""
    pose = Pose(x=0.0, y=0.0, yaw=0.0)

    with pytest.raises(TypeError, match="NumPy ndarray"):
        pose.as_np_array = [1.0, 2.0, 3.0]


@pytest.mark.parametrize(
    "value",
    [
        (1.0, 2.0, 3.0),
        "1.0, 2.0, 3.0",
        None,
    ],
)
def test_pose_setter_rejects_other_non_numpy_inputs(
    value: object,
) -> None:
    """Test rejection of tuples, strings, and None."""
    pose = Pose(x=0.0, y=0.0, yaw=0.0)

    with pytest.raises(TypeError, match="NumPy ndarray"):
        pose.as_np_array = value


@pytest.mark.parametrize(
    "value",
    [
        np.array([1.0, 2.0]),
        np.array([1.0, 2.0, 3.0, 4.0]),
        np.array([]),
        np.array([[1.0, 2.0, 3.0]]),
    ],
)
def test_pose_setter_rejects_invalid_shapes(
    value: np.ndarray,
) -> None:
    """Test that the setter rejects arrays not shaped (3,)."""
    pose = Pose(x=0.0, y=0.0, yaw=0.0)

    with pytest.raises(ValueError, match="shape"):
        pose.as_np_array = value


@pytest.mark.parametrize(
    "value",
    [
        np.array(["1.0", "2.0", "3.0"]),
        np.array(["x", "y", "z"]),
        np.array([True, False, True]),
    ],
)
def test_pose_setter_rejects_non_numeric_arrays(
    value: np.ndarray,
) -> None:
    """Test that the setter rejects arrays with non-numeric dtypes."""
    pose = Pose(x=0.0, y=0.0, yaw=0.0)

    with pytest.raises(TypeError, match="numeric values"):
        pose.as_np_array = value


@pytest.mark.parametrize(
    "value",
    [
        np.array([np.nan, 2.0, 3.0]),
        np.array([1.0, np.inf, 3.0]),
        np.array([1.0, 2.0, -np.inf]),
    ],
)
def test_pose_setter_rejects_non_finite_values(
    value: np.ndarray,
) -> None:
    """Test that the setter rejects NaN and infinite values."""
    pose = Pose(x=0.0, y=0.0, yaw=0.0)

    with pytest.raises(ValueError, match="finite values"):
        pose.as_np_array = value


def test_pose_setter_preserves_state_after_invalid_input() -> None:
    """Test that invalid input does not modify the existing pose."""
    pose = Pose(x=1.0, y=2.0, yaw=0.5)

    with pytest.raises(ValueError, match="finite values"):
        pose.as_np_array = np.array([10.0, np.nan, 30.0])

    assert pose.x == 1.0
    assert pose.y == 2.0
    assert pose.yaw == 0.5


# ------------------------------------------------------------------
# Equality
# ------------------------------------------------------------------


def test_pose_equality() -> None:
    """Test equality between poses with identical values."""
    pose_1 = Pose(x=1.0, y=2.0, yaw=0.5)
    pose_2 = Pose(x=1.0, y=2.0, yaw=0.5)

    assert pose_1 == pose_2


def test_pose_inequality() -> None:
    """Test inequality between poses with different values."""
    pose_1 = Pose(x=1.0, y=2.0, yaw=0.5)
    pose_2 = Pose(x=1.0, y=2.0, yaw=1.0)

    assert pose_1 != pose_2