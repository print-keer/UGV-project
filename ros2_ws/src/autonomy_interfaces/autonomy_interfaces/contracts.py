from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

GridCell = Tuple[int, int]

PLANNER_IDLE = "idle"
PLANNER_PLANNING = "planning"
PLANNER_SUCCESS = "success"
PLANNER_NO_PATH = "no_path"
PLANNER_ERROR = "error"

NAV_IDLE = "idle"
NAV_FOLLOWING_PATH = "following_path"
NAV_REACHED_GOAL = "reached_goal"
NAV_BLOCKED = "blocked"
NAV_ERROR = "error"

REPLAN_PATH_BLOCKED = "path_blocked"
REPLAN_GOAL_CHANGED = "goal_changed"
REPLAN_MAP_UPDATED = "map_updated"
REPLAN_EMPTY_PATH = "empty_path"
REPLAN_NO_PATH_RECOVERY = "no_path_recovery"


@dataclass(frozen=True)
class OccupancyGridMessage:
    width: int
    height: int
    resolution: float
    origin: GridCell
    data: List[int]
    frame_id: str = "map"
    source_map: str = ""
    revision: int = 0

    def cell_value(self, row: int, col: int) -> int:
        return self.data[row * self.width + col]

    def to_grid(self) -> List[List[int]]:
        return [
            self.data[row * self.width : (row + 1) * self.width]
            for row in range(self.height)
        ]


@dataclass(frozen=True)
class MissionGoalMessage:
    goal_cell: GridCell
    start_cell: Optional[GridCell] = None
    goal_id: str = "default_goal"


@dataclass(frozen=True)
class PlannedPathMessage:
    path_found: bool
    waypoints: List[GridCell] = field(default_factory=list)
    total_cost: float = 0.0
    goal_id: str = "default_goal"


@dataclass(frozen=True)
class PlannerStatusMessage:
    state: str
    message: str
    goal_id: str = "default_goal"
    visited_nodes: int = 0
    start_cell: Optional[GridCell] = None
    goal_cell: Optional[GridCell] = None
    occupancy_revision: int = 0


@dataclass(frozen=True)
class NavigationStatusMessage:
    state: str
    message: str
    current_cell: Optional[GridCell] = None
    current_waypoint_index: int = -1
    goal_id: str = "default_goal"
    path_length: int = 0


@dataclass(frozen=True)
class ReplanRequestMessage:
    reason: str
    current_cell: Optional[GridCell] = None
    goal_id: str = "default_goal"
    occupancy_revision: int = 0


@dataclass(frozen=True)
class TopicEnvelope:
    topic: str
    payload: object
