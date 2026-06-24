from __future__ import annotations

from autonomy_interfaces.contracts import OccupancyGridMessage

from .mock_maps import MockMap


def build_occupancy_grid(mock_map: MockMap, resolution: float = 1.0) -> OccupancyGridMessage:
    height = len(mock_map.grid)
    width = len(mock_map.grid[0]) if height else 0
    flattened = [cell for row in mock_map.grid for cell in row]
    return OccupancyGridMessage(
        width=width,
        height=height,
        resolution=resolution,
        origin=mock_map.start,
        data=flattened,
        source_map=mock_map.name,
    )
