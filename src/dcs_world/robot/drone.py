from collections import deque
from enum import Enum, auto

from dcs_world.geometry.pose import Pose
from dcs_world.communication.messages import (
    ExplorationTaskMessage,
    ExplorationResponseMessage,
    ExplorationResponseStatus,
)

from .robot import Robot
from .utils import RobotConfig
from .navigation.navigation_controller import NavigationController


# ============================================================
# DRONE STATE
# ============================================================

class DroneState(Enum):
    IDLE = auto()
    EXPLORING = auto()
    RETURNING = auto()
    ERROR = auto()


# ============================================================
# DRONE
# ============================================================

class Drone(Robot):
    ROBOT_TYPE = "Drone"

    def __init__(
        self,
        id: str | None = None,
        init_pose: Pose | None = None,
        init_soc: float = 100.0,
        config: RobotConfig = Robot.DEFAULT_CONFIG,
    ):
        super().__init__(
            id=id,
            init_pose=init_pose,
            init_soc=init_soc,
            config=config,
        )

        self.state = DroneState.IDLE

        # Navigation
        self._targets: deque[Pose] = deque()
        self._current_target: Pose | None = None

        self.navigation_controller = NavigationController(
            max_speed=self.config.max_speed,
        )

        # Task management
        self._current_task_id: str | None = None
        self._pending_task_responses: deque[ExplorationResponseMessage] = deque()

    # ========================================================
    # PROPERTIES
    # ========================================================

    @property
    def current_target(self) -> Pose | None:
        """Return a copy of the current navigation target."""
        return self._current_target.copy() if self._current_target else None

    @property
    def remaining_targets(self) -> int:
        """Number of targets remaining after the current target."""
        return len(self._targets)

    @property
    def current_task_id(self) -> str | None:
        """ID of the currently executing exploration task."""
        return self._current_task_id

    # ========================================================
    # TASK RESPONSE MANAGEMENT
    # ========================================================

    def consume_task_response(self) -> ExplorationResponseMessage | None:
        """
        Retrieve the next pending task response.

        Responses are consumed exactly once.
        Returns None when there are no pending responses.
        """
        if not self._pending_task_responses:
            return None

        return self._pending_task_responses.popleft()

    def _queue_task_response(
        self,
        status: ExplorationResponseStatus,
        reason: str = "",
    ) -> None:
        """Queue an event-driven response for the current task."""

        if self._current_task_id is None:
            return

        response = ExplorationResponseMessage(
            task_id=self._current_task_id,
            drone_id=self.id,
            status=status,
            reason=reason,
        )

        self._pending_task_responses.append(response)

    # ========================================================
    # EXPLORATION TASK ASSIGNMENT
    # ========================================================

    def assign_exploration(
        self,
        request: ExplorationTaskMessage,
    ) -> ExplorationResponseMessage:
        """Validate and accept or reject an exploration task."""

        if self.state != DroneState.IDLE:
            return ExplorationResponseMessage(
                task_id=request.task_id,
                drone_id=self.id,
                status=ExplorationResponseStatus.REJECTED,
                reason=f"Drone is currently {self.state.name}.",
            )

        if not request.targets:
            return ExplorationResponseMessage(
                task_id=request.task_id,
                drone_id=self.id,
                status=ExplorationResponseStatus.REJECTED,
                reason="No exploration targets provided.",
            )

        # Store the task and its targets.
        self._current_task_id = request.task_id

        self._targets = deque(
            target.copy() for target in request.targets
        )

        # Start exploration.
        self.state = DroneState.EXPLORING
        self._select_next_target()

        return ExplorationResponseMessage(
            task_id=request.task_id,
            drone_id=self.id,
            status=ExplorationResponseStatus.ACCEPTED,
            reason="Exploration task accepted.",
        )

    # ========================================================
    # EXPLORATION TARGET MANAGEMENT
    # ========================================================

    def _select_next_target(self) -> None:
        """Select the next target in the exploration sequence."""

        if not self._targets:
            self._current_target = None
            self._complete_task()
            return

        self._current_target = self._targets.popleft()

    def complete_current_target(self) -> None:
        """Mark the current target as reached and select the next one."""

        if self.state != DroneState.EXPLORING:
            raise RuntimeError("Drone is not currently exploring.")

        if self._current_target is None:
            raise RuntimeError("No active exploration target.")

        self._select_next_target()

    # ========================================================
    # TASK COMPLETION AND CANCELLATION
    # ========================================================

    def _complete_task(self) -> None:
        """Complete the current task and queue a completion response."""

        self._queue_task_response(
            status=ExplorationResponseStatus.COMPLETED,
            reason="All exploration targets reached.",
        )

        self._current_task_id = None
        self.state = DroneState.IDLE

    def _fail_task(self, reason: str) -> None:
        """Mark the current task as failed and queue a response."""

        self._queue_task_response(
            status=ExplorationResponseStatus.FAILED,
            reason=reason,
        )

        self._targets.clear()
        self._current_target = None
        self._current_task_id = None
        self.state = DroneState.ERROR

    def cancel_task(self) -> None:
        """Cancel the current task and clear all assigned targets."""

        self._targets.clear()
        self._current_target = None
        self._current_task_id = None
        self.state = DroneState.IDLE

    # ========================================================
    # MAIN CONTROL LOOP
    # ========================================================

    def run(self, dt: float) -> None:
        """Execute one control cycle."""

        if self.state == DroneState.IDLE:
            return

        if self.state == DroneState.EXPLORING:
            self._execute_exploration(dt)

        elif self.state == DroneState.RETURNING:
            self._execute_return(dt)

        elif self.state == DroneState.ERROR:
            return

    # ========================================================
    # EXPLORATION BEHAVIOR
    # ========================================================

    def _execute_exploration(self, dt: float) -> None:
        """Execute one exploration control cycle."""

        if self._current_target is None:
            self._complete_task()
            return

        cmd_vel = self.navigation_controller.compute_velocity(
            current_pose=self.pose,
            target_pose=self._current_target,
        )

        self.move(cmd_vel, dt)

        if self.navigation_controller.is_goal_reached(
            current_pose=self.pose,
            target_pose=self._current_target,
        ):
            self.complete_current_target()

    # ========================================================
    # RETURN-TO-BASE BEHAVIOR
    # ========================================================

    def _execute_return(self, dt: float) -> None:
        """Execute one return-to-base control cycle."""
        # To be implemented.
        pass