from __future__ import annotations

from autonomy_interfaces.contracts import OccupancyGridMessage, SensorObservationMessage

from .map_provider import MapProvider


class SensorFusionEngine:
    """Applies sensor observations onto the occupancy grid as new obstacle updates."""

    def __init__(self, map_provider: MapProvider | None = None) -> None:
        self.map_provider = map_provider or MapProvider()

    def apply_observation(
        self,
        occupancy_grid: OccupancyGridMessage,
        observation: SensorObservationMessage,
    ) -> OccupancyGridMessage:
        if not observation.detected_cells:
            return occupancy_grid
        bounded_cells = [
            cell
            for cell in observation.detected_cells
            if 0 <= cell[0] < occupancy_grid.height and 0 <= cell[1] < occupancy_grid.width
        ]
        if not bounded_cells:
            return occupancy_grid
        return self.map_provider.clone_with_obstacles(
            occupancy_grid,
            bounded_cells,
        )
