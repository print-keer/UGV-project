from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from autonomy_interfaces.contracts import (
    NAV_BLOCKED,
    NAV_FOLLOWING_PATH,
    NAV_REACHED_GOAL,
    MotionCommandMessage,
    REPLAN_NO_PATH_RECOVERY,
    REPLAN_PATH_BLOCKED,
    REPLAN_EMPTY_PATH,
    NavigationStatusMessage,
    PlannedPathMessage,
    ReplanRequestMessage,
)

GridCell = Tuple[int, int]


@dataclass
class NavigationReport:
    accepted: bool
    waypoint_count: int
    message: str
    waypoints: List[GridCell]
    status: NavigationStatusMessage
    replan_request: Optional[ReplanRequestMessage] = None


@dataclass(frozen=True)
class NavigationStep:
    current_cell: GridCell
    waypoint_index: int
    reached_goal: bool


@dataclass
class NavigationExecution:
    report: NavigationReport
    steps: List[NavigationStep]
    motion_commands: List[MotionCommandMessage]
    reached_goal: bool


class PathFollower:
    """Simulation-first waypoint follower for Person 1 mission execution."""

    def __init__(self, nominal_linear_velocity: float = 0.5) -> None:
        self.nominal_linear_velocity = nominal_linear_velocity

    def consume_path(self, planned_path: PlannedPathMessage) -> NavigationReport:
        return self.follow_path(planned_path).report

    def follow_path(
        self,
        planned_path: PlannedPathMessage,
        blocked_cell: GridCell | None = None,
    ) -> NavigationExecution:
        if not planned_path.waypoints:
            stop_command = MotionCommandMessage(
                command_type="hold_position",
                stop=True,
                goal_id=planned_path.goal_id,
                sequence_id=0,
            )
            report = NavigationReport(
                False,
                0,
                "No path available for navigation.",
                [],
                NavigationStatusMessage(
                    state=NAV_BLOCKED,
                    message="Navigation blocked because planner returned no path.",
                    goal_id=planned_path.goal_id,
                    path_length=0,
                ),
                ReplanRequestMessage(
                    reason=REPLAN_NO_PATH_RECOVERY if planned_path.path_found is False else REPLAN_EMPTY_PATH,
                    goal_id=planned_path.goal_id,
                ),
            )
            return NavigationExecution(report=report, steps=[], motion_commands=[stop_command], reached_goal=False)

        steps: List[NavigationStep] = []
        motion_commands: List[MotionCommandMessage] = []
        for index, cell in enumerate(planned_path.waypoints):
            reached_goal = index == len(planned_path.waypoints) - 1
            steps.append(
                NavigationStep(
                    current_cell=cell,
                    waypoint_index=index,
                    reached_goal=reached_goal,
                )
            )
            if index > 0:
                motion_commands.append(
                    MotionCommandMessage(
                        command_type="step_to_cell",
                        target_cell=cell,
                        linear_velocity=self.nominal_linear_velocity,
                        angular_velocity=0.0,
                        stop=False,
                        goal_id=planned_path.goal_id,
                        sequence_id=len(motion_commands),
                    )
                )
            if blocked_cell is not None and cell == blocked_cell:
                motion_commands.append(
                    MotionCommandMessage(
                        command_type="emergency_stop",
                        target_cell=blocked_cell,
                        linear_velocity=0.0,
                        angular_velocity=0.0,
                        stop=True,
                        goal_id=planned_path.goal_id,
                        sequence_id=len(motion_commands),
                    )
                )
                report = NavigationReport(
                    accepted=False,
                    waypoint_count=len(planned_path.waypoints),
                    message=f"Navigation blocked at cell {blocked_cell}.",
                    waypoints=planned_path.waypoints,
                    status=NavigationStatusMessage(
                        state=NAV_BLOCKED,
                        message=f"Blocked waypoint detected at {blocked_cell}.",
                        current_cell=blocked_cell,
                        current_waypoint_index=index,
                        goal_id=planned_path.goal_id,
                        path_length=len(planned_path.waypoints),
                    ),
                    replan_request=ReplanRequestMessage(
                        reason=REPLAN_PATH_BLOCKED,
                        current_cell=blocked_cell,
                        goal_id=planned_path.goal_id,
                    ),
                )
                return NavigationExecution(
                    report=report,
                    steps=steps,
                    motion_commands=motion_commands,
                    reached_goal=False,
                )

        final_step = steps[-1]
        motion_commands.append(
            MotionCommandMessage(
                command_type="stop_at_goal",
                target_cell=final_step.current_cell,
                linear_velocity=0.0,
                angular_velocity=0.0,
                stop=True,
                goal_id=planned_path.goal_id,
                sequence_id=len(motion_commands),
            )
        )
        report = NavigationReport(
            accepted=True,
            waypoint_count=len(planned_path.waypoints),
            message="Navigation reached the goal waypoint sequence.",
            waypoints=planned_path.waypoints,
            status=NavigationStatusMessage(
                state=NAV_REACHED_GOAL if final_step.reached_goal else NAV_FOLLOWING_PATH,
                message="Navigation reached the goal." if final_step.reached_goal else "Navigation is following the path.",
                current_cell=final_step.current_cell,
                current_waypoint_index=final_step.waypoint_index,
                goal_id=planned_path.goal_id,
                path_length=len(planned_path.waypoints),
            ),
        )
        return NavigationExecution(
            report=report,
            steps=steps,
            motion_commands=motion_commands,
            reached_goal=final_step.reached_goal,
        )

    def detect_blocked_waypoint(
        self,
        planned_path: PlannedPathMessage,
        blocked_cell: GridCell,
    ) -> NavigationReport:
        return self.follow_path(planned_path, blocked_cell=blocked_cell).report
