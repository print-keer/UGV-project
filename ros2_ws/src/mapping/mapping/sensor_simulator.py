from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from autonomy_interfaces.contracts import SensorObservationMessage

from .mock_maps import MockMap


@dataclass(frozen=True)
class SensorScenario:
    lidar_cells: List[tuple[int, int]] = field(default_factory=list)
    ultrasonic_cells: List[tuple[int, int]] = field(default_factory=list)


class SensorSimulator:
    """Generates deterministic LiDAR-like and ultrasonic-like observations."""

    def __init__(self, mock_map: MockMap) -> None:
        self.mock_map = mock_map
        self.sequence_id = 0

    def observe(self, scenario: SensorScenario) -> list[SensorObservationMessage]:
        observations: list[SensorObservationMessage] = []
        if scenario.lidar_cells:
            observations.append(
                SensorObservationMessage(
                    sensor_type="lidar",
                    detected_cells=list(scenario.lidar_cells),
                    source_map=self.mock_map.name,
                    sequence_id=self.sequence_id,
                )
            )
            self.sequence_id += 1
        if scenario.ultrasonic_cells:
            observations.append(
                SensorObservationMessage(
                    sensor_type="ultrasonic",
                    detected_cells=list(scenario.ultrasonic_cells),
                    source_map=self.mock_map.name,
                    sequence_id=self.sequence_id,
                )
            )
            self.sequence_id += 1
        return observations

