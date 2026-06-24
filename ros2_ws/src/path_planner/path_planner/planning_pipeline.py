from __future__ import annotations

from autonomy_interfaces.contracts import (
    PLANNER_NO_PATH,
    PLANNER_SUCCESS,
    MissionGoalMessage,
    OccupancyGridMessage,
    PlannedPathMessage,
    PlannerStatusMessage,
)

from .astar import AStarPlanner
from .types import GridCell


class PlanningPipeline:
    """Adapter that turns planner core results into stable pipeline contracts."""

    def __init__(self, planner: AStarPlanner | None = None) -> None:
        self.planner = planner or AStarPlanner()

    def plan_for_goal(
        self,
        occupancy_grid: OccupancyGridMessage,
        mission_goal: MissionGoalMessage,
    ) -> tuple[PlannedPathMessage, PlannerStatusMessage]:
        start_cell: GridCell = mission_goal.start_cell or occupancy_grid.origin
        result = self.planner.plan(
            occupancy_grid.to_grid(),
            start_cell,
            mission_goal.goal_cell,
        )
        path_message = PlannedPathMessage(
            path_found=result.path_found,
            waypoints=result.path,
            total_cost=result.total_cost,
            goal_id=mission_goal.goal_id,
        )
        state = PLANNER_SUCCESS if result.path_found else PLANNER_NO_PATH
        status_message = PlannerStatusMessage(
            state=state,
            message=result.message,
            goal_id=mission_goal.goal_id,
            visited_nodes=result.visited_nodes,
            start_cell=start_cell,
            goal_cell=mission_goal.goal_cell,
            occupancy_revision=occupancy_grid.revision,
        )
        return path_message, status_message
