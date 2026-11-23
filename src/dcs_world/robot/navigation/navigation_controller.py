import math

from dcs_world.geometry.pose import Pose
from dcs_world.geometry.twist import Twist


class NavigationController:
    """Position-based proportional navigation controller."""

    def __init__(
        self,
        max_speed: float = 1.0,
        max_vertical_speed: float = 0.5,
        max_yaw_rate: float = 1.0,
        kp_position: float = 1.0,
        kp_yaw: float = 1.0,
        position_tolerance: float = 0.1,
        altitude_tolerance: float = 0.1,
        yaw_tolerance: float = 0.1,
    ):
        self.max_speed = max_speed
        self.max_vertical_speed = max_vertical_speed
        self.max_yaw_rate = max_yaw_rate

        self.kp_position = kp_position
        self.kp_yaw = kp_yaw

        self.position_tolerance = position_tolerance
        self.altitude_tolerance = altitude_tolerance
        self.yaw_tolerance = yaw_tolerance

    @staticmethod
    def _clamp(value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(value, maximum))

    @staticmethod
    def _wrap_angle(angle: float) -> float:
        return (angle + math.pi) % (2.0 * math.pi) - math.pi

    def compute_velocity(
        self,
        current_pose: Pose,
        target_pose: Pose,
    ) -> Twist:
        """Compute a body-frame velocity command toward the target."""

        # Position error in the world frame
        dx = target_pose.position.x - current_pose.position.x
        dy = target_pose.position.y - current_pose.position.y
        dz = target_pose.position.z - current_pose.position.z

        # Proportional position controller
        vx_world = self.kp_position * dx
        vy_world = self.kp_position * dy
        vz = self.kp_position * dz

        # Limit horizontal speed magnitude
        speed = math.hypot(vx_world, vy_world)

        if speed > self.max_speed:
            scale = self.max_speed / speed
            vx_world *= scale
            vy_world *= scale

        # Convert world-frame velocity into the drone's body frame.
        # Robot.move() expects body-frame linear velocities.
        yaw = current_pose.yaw

        vx_body = math.cos(yaw) * vx_world + math.sin(yaw) * vy_world
        vy_body = -math.sin(yaw) * vx_world + math.cos(yaw) * vy_world

        # Limit vertical speed
        vz = self._clamp(
            vz,
            -self.max_vertical_speed,
            self.max_vertical_speed,
        )

        # Proportional yaw controller
        yaw_error = self._wrap_angle(
            target_pose.yaw - current_pose.yaw
        )

        yaw_rate = self._clamp(
            self.kp_yaw * yaw_error,
            -self.max_yaw_rate,
            self.max_yaw_rate,
        )

        return Twist(
            linear=(vx_body, vy_body, vz),
            angular=(0.0, 0.0, yaw_rate),
        )

    def is_goal_reached(
        self,
        current_pose: Pose,
        target_pose: Pose,
    ) -> bool:
        """Check whether the drone has reached the target pose."""

        dx = target_pose.position.x - current_pose.position.x
        dy = target_pose.position.y - current_pose.position.y
        dz = target_pose.position.z - current_pose.position.z

        horizontal_distance = math.hypot(dx, dy)
        yaw_error = abs(
            self._wrap_angle(target_pose.yaw - current_pose.yaw)
        )

        return (
            horizontal_distance <= self.position_tolerance
            and abs(dz) <= self.altitude_tolerance
            and yaw_error <= self.yaw_tolerance
        )