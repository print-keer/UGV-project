from __future__ import annotations

from autonomy_interfaces.contracts import OccupancyGridMessage

from .mock_maps import MockMap
from .occupancy_grid import build_occupancy_grid


class MapProvider:
    """Simulation-first stand-in for a future ROS2 occupancy-grid publisher."""

    def publish_map(self, mock_map: MockMap, revision: int = 0) -> OccupancyGridMessage:
        occupancy_grid = build_occupancy_grid(mock_map)
        return OccupancyGridMessage(
            width=occupancy_grid.width,
            height=occupancy_grid.height,
            resolution=occupancy_grid.resolution,
            origin=occupancy_grid.origin,
            data=occupancy_grid.data,
            frame_id=occupancy_grid.frame_id,
            source_map=occupancy_grid.source_map,
            revision=revision,
        )

    def clone_with_obstacle(
        self,
        occupancy_grid: OccupancyGridMessage,
        blocked_cell: tuple[int, int],
    ) -> OccupancyGridMessage:
        row, col = blocked_cell
        data = list(occupancy_grid.data)
        data[row * occupancy_grid.width + col] = 1
        return OccupancyGridMessage(
            width=occupancy_grid.width,
            height=occupancy_grid.height,
            resolution=occupancy_grid.resolution,
            origin=occupancy_grid.origin,
            data=data,
            frame_id=occupancy_grid.frame_id,
            source_map=occupancy_grid.source_map,
            revision=occupancy_grid.revision + 1,
        )

    def clone_with_obstacles(
        self,
        occupancy_grid: OccupancyGridMessage,
        blocked_cells: list[tuple[int, int]],
    ) -> OccupancyGridMessage:
        updated_grid = occupancy_grid
        for blocked_cell in blocked_cells:
            updated_grid = self.clone_with_obstacle(updated_grid, blocked_cell)
        return updated_grid
