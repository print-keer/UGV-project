from __future__ import annotations

from dataclasses import dataclass
from typing import List

from autonomy_interfaces.contracts import OccupancyGridMessage

from .map_provider import MapProvider
from .mock_maps import MockMap


@dataclass(frozen=True)
class DynamicWorldStep:
    occupancy_grid: OccupancyGridMessage
    applied_obstacle: tuple[int, int] | None
    step_index: int
    scenario_complete: bool


class DynamicWorld:
    """Applies a deterministic sequence of obstacle updates to a mock map."""

    def __init__(self, mock_map: MockMap, map_provider: MapProvider | None = None) -> None:
        self.mock_map = mock_map
        self.map_provider = map_provider or MapProvider()
        self.base_grid = self.map_provider.publish_map(mock_map, revision=0)
        self._applied_index = 0
        self._current_grid = self.base_grid

    @property
    def current_grid(self) -> OccupancyGridMessage:
        return self._current_grid

    @property
    def remaining_updates(self) -> int:
        return max(0, len(self.mock_map.dynamic_obstacles) - self._applied_index)

    def reset(self) -> None:
        self._applied_index = 0
        self._current_grid = self.base_grid

    def snapshot(self) -> DynamicWorldStep:
        return DynamicWorldStep(
            occupancy_grid=self._current_grid,
            applied_obstacle=None,
            step_index=self._applied_index,
            scenario_complete=self.remaining_updates == 0,
        )

    def advance(self) -> DynamicWorldStep:
        if self._applied_index >= len(self.mock_map.dynamic_obstacles):
            return self.snapshot()

        obstacle = self.mock_map.dynamic_obstacles[self._applied_index]
        self._current_grid = self.map_provider.clone_with_obstacle(self._current_grid, obstacle)
        self._applied_index += 1
        return DynamicWorldStep(
            occupancy_grid=self._current_grid,
            applied_obstacle=obstacle,
            step_index=self._applied_index,
            scenario_complete=self.remaining_updates == 0,
        )

    def full_timeline(self) -> List[DynamicWorldStep]:
        timeline = [self.snapshot()]
        while self.remaining_updates > 0:
            timeline.append(self.advance())
        return timeline

