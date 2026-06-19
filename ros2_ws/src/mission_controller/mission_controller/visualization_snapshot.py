from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from autonomy_interfaces.contracts import (
    MissionGoalMessage,
    NavigationStatusMessage,
    OccupancyGridMessage,
    PlannedPathMessage,
)


@dataclass(frozen=True)
class VisualizationSnapshot:
    map_width: int
    map_height: int
    occupied_cells: int
    unknown_cells: int
    path_length: int
    goal_cell: Optional[tuple[int, int]]
    current_cell: Optional[tuple[int, int]]
    reached_goal: bool


def build_visualization_snapshot(
    occupancy_grid: OccupancyGridMessage,
    planned_path: PlannedPathMessage | None = None,
    mission_goal: MissionGoalMessage | None = None,
    navigation_status: NavigationStatusMessage | None = None,
) -> VisualizationSnapshot:
    occupied_cells = sum(1 for value in occupancy_grid.data if value == 1)
    unknown_cells = sum(1 for value in occupancy_grid.data if value == 2)
    path_length = len(planned_path.waypoints) if planned_path is not None else 0
    goal_cell = mission_goal.goal_cell if mission_goal is not None else None
    current_cell = navigation_status.current_cell if navigation_status is not None else None
    reached_goal = (
        navigation_status is not None and navigation_status.state == "reached_goal"
    )
    return VisualizationSnapshot(
        map_width=occupancy_grid.width,
        map_height=occupancy_grid.height,
        occupied_cells=occupied_cells,
        unknown_cells=unknown_cells,
        path_length=path_length,
        goal_cell=goal_cell,
        current_cell=current_cell,
        reached_goal=reached_goal,
    )

