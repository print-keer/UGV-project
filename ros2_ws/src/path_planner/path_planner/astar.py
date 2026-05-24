from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from math import inf
from typing import Dict, Iterable, Optional

from .types import EdgeCostFn, Grid, GridCell, PlanResult, PlannerConfig


@dataclass(order=True)
class _QueueItem:
    priority: float
    cell: GridCell


class AStarPlanner:
    """Grid-based A* planner with an isolated cost model for future threat logic."""

    def __init__(
        self,
        config: Optional[PlannerConfig] = None,
        edge_cost_fn: Optional[EdgeCostFn] = None,
    ) -> None:
        self.config = config or PlannerConfig()
        self.edge_cost_fn = edge_cost_fn or self._default_edge_cost

    def plan(self, grid: Grid, start: GridCell, goal: GridCell) -> PlanResult:
        if not self._in_bounds(grid, start) or not self._in_bounds(grid, goal):
            return PlanResult(False, message="Start or goal is out of bounds.")
        if not self._is_traversable(grid, start):
            return PlanResult(False, message="Start cell is not traversable.")
        if not self._is_traversable(grid, goal):
            return PlanResult(False, message="Goal cell is not traversable.")

        open_set = [_QueueItem(0.0, start)]
        came_from: Dict[GridCell, GridCell] = {}
        g_score: Dict[GridCell, float] = {start: 0.0}
        visited_nodes = 0

        while open_set:
            current = heappop(open_set).cell
            visited_nodes += 1

            if current == goal:
                path = self._reconstruct_path(came_from, current)
                return PlanResult(
                    path_found=True,
                    path=path,
                    total_cost=g_score[current],
                    visited_nodes=visited_nodes,
                    message="Path found.",
                )

            for neighbor in self._neighbors(grid, current):
                tentative_cost = g_score[current] + self.edge_cost_fn(
                    neighbor,
                    grid[neighbor[0]][neighbor[1]],
                )
                if tentative_cost >= g_score.get(neighbor, inf):
                    continue
                came_from[neighbor] = current
                g_score[neighbor] = tentative_cost
                priority = tentative_cost + self._heuristic(neighbor, goal)
                heappush(open_set, _QueueItem(priority, neighbor))

        return PlanResult(
            path_found=False,
            visited_nodes=visited_nodes,
            message="No path found between start and goal.",
        )

    def _default_edge_cost(self, cell: GridCell, cell_value: int) -> float:
        del cell
        base_cost = self.config.straight_step_cost
        if cell_value == self.config.unknown_value:
            return base_cost + self.config.unknown_cell_penalty
        return base_cost

    def _neighbors(self, grid: Grid, cell: GridCell) -> Iterable[GridCell]:
        row, col = cell
        candidates = (
            (row - 1, col),
            (row + 1, col),
            (row, col - 1),
            (row, col + 1),
        )
        for neighbor in candidates:
            if self._in_bounds(grid, neighbor) and self._is_traversable(grid, neighbor):
                yield neighbor

    @staticmethod
    def _heuristic(a: GridCell, b: GridCell) -> float:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def _in_bounds(grid: Grid, cell: GridCell) -> bool:
        row, col = cell
        return 0 <= row < len(grid) and 0 <= col < len(grid[0])

    def _is_traversable(self, grid: Grid, cell: GridCell) -> bool:
        value = grid[cell[0]][cell[1]]
        if value == self.config.obstacle_value:
            return False
        if value == self.config.unknown_value and not self.config.allow_unknown_cells:
            return False
        return True

    @staticmethod
    def _reconstruct_path(came_from: Dict[GridCell, GridCell], current: GridCell) -> list[GridCell]:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

