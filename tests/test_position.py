import numpy as np
import pytest

from dcs_world.geometry.position import Position


def test_position_initialization() -> None:
    """Test initialization with the provided coordinates."""
    position = Position(x=1.5, y=2.5)

    assert position.x == 1.5
    assert position.y == 2.5


def test_position_as_np_array() -> None:
    """Test conversion to a NumPy array."""
    position = Position(x=1.5, y=2.5)

    np.testing.assert_array_equal(
        position.as_np_array,
        np.array([1.5, 2.5]),
    )


def test_position_as_np_array_returns_independent_array() -> None:
    """Test that modifying the array doesn't change the position."""
    position = Position(x=1.0, y=2.0)

    array = position.as_np_array
    array[0] = 100.0

    assert position.x == 1.0
    assert position.y == 2.0


def test_position_equality() -> None:
    """Test equality between positions with identical coordinates."""
    position_1 = Position(x=1.0, y=2.0)
    position_2 = Position(x=1.0, y=2.0)

    assert position_1 == position_2


def test_position_inequality() -> None:
    """Test inequality between positions with different coordinates."""
    position_1 = Position(x=1.0, y=2.0)
    position_2 = Position(x=3.0, y=4.0)

    assert position_1 != position_2