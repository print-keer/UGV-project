from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from autonomy_interfaces.contracts import (
    NAV_BLOCKED,
    NAV_FOLLOWING_PATH,
    NAV_REACHED_GOAL,
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


class PathFollower:
    """Placeholder path consumer for milestone one simulation flow."""

    def consume_path(self, planned_path: PlannedPathMessage) -> NavigationReport:
        if not planned_path.waypoints:
            return NavigationReport(
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
        final_cell = planned_path.waypoints[-1]
        return NavigationReport(
            accepted=True,
            waypoint_count=len(planned_path.waypoints),
            message="Path accepted by navigation layer.",
            waypoints=planned_path.waypoints,
            status=NavigationStatusMessage(
                state=NAV_REACHED_GOAL if len(planned_path.waypoints) == 1 else NAV_FOLLOWING_PATH,
                message="Navigation accepted the planned path.",
                current_cell=final_cell,
                current_waypoint_index=len(planned_path.waypoints) - 1,
                goal_id=planned_path.goal_id,
                path_length=len(planned_path.waypoints),
            ),
        )

    def detect_blocked_waypoint(
        self,
        planned_path: PlannedPathMessage,
        blocked_cell: GridCell,
    ) -> NavigationReport:
        return NavigationReport(
            accepted=False,
            waypoint_count=len(planned_path.waypoints),
            message=f"Navigation blocked at cell {blocked_cell}.",
            waypoints=planned_path.waypoints,
            status=NavigationStatusMessage(
                state=NAV_BLOCKED,
                message=f"Blocked waypoint detected at {blocked_cell}.",
                current_cell=blocked_cell,
                current_waypoint_index=planned_path.waypoints.index(blocked_cell)
                if blocked_cell in planned_path.waypoints
                else -1,
                goal_id=planned_path.goal_id,
                path_length=len(planned_path.waypoints),
            ),
            replan_request=ReplanRequestMessage(
                reason=REPLAN_PATH_BLOCKED,
                current_cell=blocked_cell,
                goal_id=planned_path.goal_id,
            ),
        )
