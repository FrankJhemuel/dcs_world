import json

from dcs_world.geometry.pose import Position
from dcs_world.observation import DroneObservation, RobotObservation, GroundRobotObservation


def main():

    # Create observations
    drone_obs = DroneObservation(
        timestamp=1.5,
        type="poi",
        building_position=Position(x=1.0, y=2.0)
    )

    robot_obs = RobotObservation(
        timestamp=2.0,
        type="obstacle",
        position=Position(x=3.0, y=4.0)
    )

    ground_robot_obs = GroundRobotObservation(
        timestamp=3.0,
        type="civilian",
        building_position=Position(x=5.0, y=6.0),
        n_civilians=4
    )

    observations = [
        drone_obs,
        robot_obs,
        ground_robot_obs
    ]

    for obs in observations:

        print(f"\n=== {obs.__class__.__name__} ===")

        # Dictionary test
        obs_dict = obs.to_dict()

        print("\nDICTIONARY:")
        print(obs_dict)

        print("\nTYPES:")
        print(type(obs_dict))

        # Determine position field
        position_key = (
            "position"
            if isinstance(obs, RobotObservation)
            else "building_position"
        )

        print(type(obs_dict[position_key]))

        # JSON test
        obs_json = obs.to_json()

        print("\nJSON:")
        print(json.dumps(json.loads(obs_json), indent=4))

        # Assertions
        assert isinstance(obs_dict, dict)
        assert isinstance(obs_json, str)
        assert isinstance(obs_dict[position_key], dict)

        if isinstance(obs, GroundRobotObservation):
            assert isinstance(obs_dict["n_civilians"], int)

    print("\nAll tests passed!")


if __name__ == "__main__":
    main()