import json

import pytest

from dcs_world.robot.robot_utils import RobotConfig, RobotStatus


def test_robot_config_from_json() -> None:
    json_str = json.dumps({
        "id": "robot_01",
        "max_speed": 2.0,
        "max_accel": 1.0,
    })

    config = RobotConfig.from_json(json_str)

    assert config.id == "robot_01"
    assert config.max_speed == 2.0
    assert config.max_accel == 1.0


def test_robot_config_from_json_missing_field() -> None:
    json_str = '{"id": "robot_01", "max_speed": 2.0}'

    with pytest.raises(ValueError, match="Invalid JSON"):
        RobotConfig.from_json(json_str)


def test_robot_config_from_invalid_json() -> None:
    with pytest.raises(ValueError, match="Invalid JSON"):
        RobotConfig.from_json("{invalid json}")


def test_robot_config_from_json_wrong_structure() -> None:
    with pytest.raises(ValueError, match="Invalid JSON"):
        RobotConfig.from_json("[]")


def test_robot_config_dataclass_equality() -> None:
    config1 = RobotConfig(
        id="robot_01",
        max_speed=2.0,
        max_accel=1.0,
    )
    config2 = RobotConfig(
        id="robot_01",
        max_speed=2.0,
        max_accel=1.0,
    )

    assert config1 == config2