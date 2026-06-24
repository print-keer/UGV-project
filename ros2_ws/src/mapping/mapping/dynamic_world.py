from __future__ import annotations

from dataclasses import dataclass
from typing import List

from autonomy_interfaces.contracts import OccupancyGridMessage, SensorObservationMessage

from .map_provider import MapProvider
from .mock_maps import MockMap
from .sensor_fusion import SensorFusionEngine
from .sensor_simulator import SensorScenario, SensorSimulator


@dataclass(frozen=True)
class DynamicWorldStep:
    occupancy_grid: OccupancyGridMessage
    applied_obstacle: tuple[int, int] | None
    step_index: int
    scenario_complete: bool
    sensor_observations: List[SensorObservationMessage] | None = None


class DynamicWorld:
    """Applies a deterministic sequence of obstacle updates to a mock map."""

    def __init__(self, mock_map: MockMap, map_provider: MapProvider | None = None) -> None:
        self.mock_map = mock_map
        self.map_provider = map_provider or MapProvider()
        self.sensor_fusion = SensorFusionEngine(self.map_provider)
        self.sensor_simulator = SensorSimulator(mock_map)
        self.base_grid = self.map_provider.publish_map(mock_map, revision=0)
        self._applied_index = 0
        self._current_grid = self.base_grid
        self._sensor_index = 0

    @property
    def current_grid(self) -> OccupancyGridMessage:
        return self._current_grid

    @property
    def remaining_updates(self) -> int:
        return max(0, len(self.mock_map.dynamic_obstacles) - self._applied_index)

    def reset(self) -> None:
        self._applied_index = 0
        self._sensor_index = 0
        self._current_grid = self.base_grid

    def snapshot(self) -> DynamicWorldStep:
        return DynamicWorldStep(
            occupancy_grid=self._current_grid,
            applied_obstacle=None,
            step_index=self._applied_index,
            scenario_complete=self.remaining_updates == 0,
            sensor_observations=[],
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
            sensor_observations=[],
        )

    def sensor_scenario_remaining(self) -> bool:
        return self._sensor_index < max(
            len(self.mock_map.lidar_observations),
            len(self.mock_map.ultrasonic_observations),
        )

    def advance_sensor_step(self) -> DynamicWorldStep:
        lidar_cells = (
            self.mock_map.lidar_observations[self._sensor_index]
            if self._sensor_index < len(self.mock_map.lidar_observations)
            else []
        )
        ultrasonic_cells = (
            self.mock_map.ultrasonic_observations[self._sensor_index]
            if self._sensor_index < len(self.mock_map.ultrasonic_observations)
            else []
        )
        scenario = SensorScenario(
            lidar_cells=list(lidar_cells),
            ultrasonic_cells=list(ultrasonic_cells),
        )
        observations = self.sensor_simulator.observe(scenario)
        updated_grid = self._current_grid
        for observation in observations:
            updated_grid = self.sensor_fusion.apply_observation(updated_grid, observation)
        self._current_grid = updated_grid
        self._sensor_index += 1
        return DynamicWorldStep(
            occupancy_grid=self._current_grid,
            applied_obstacle=None,
            step_index=self._sensor_index,
            scenario_complete=not self.sensor_scenario_remaining(),
            sensor_observations=observations,
        )

    def apply_external_observation(self, observation: SensorObservationMessage) -> DynamicWorldStep:
        self._current_grid = self.sensor_fusion.apply_observation(self._current_grid, observation)
        return DynamicWorldStep(
            occupancy_grid=self._current_grid,
            applied_obstacle=None,
            step_index=observation.sequence_id,
            scenario_complete=self.remaining_updates == 0 and not self.sensor_scenario_remaining(),
            sensor_observations=[observation],
        )

    def full_timeline(self) -> List[DynamicWorldStep]:
        timeline = [self.snapshot()]
        while self.remaining_updates > 0:
            timeline.append(self.advance())
        return timeline
