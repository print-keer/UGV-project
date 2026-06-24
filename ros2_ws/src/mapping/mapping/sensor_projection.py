from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from autonomy_interfaces.contracts import GridCell, SensorObservationMessage


@dataclass(frozen=True)
class LidarProjectionConfig:
    origin_cell: GridCell = (0, 0)
    resolution_m: float = 1.0
    angle_min_rad: float = 0.0
    angle_increment_rad: float = 0.0
    min_range_m: float = 0.05
    max_range_m: float = 8.0
    source_map: str = ""


@dataclass(frozen=True)
class UltrasonicProjectionConfig:
    origin_cell: GridCell = (0, 0)
    resolution_m: float = 1.0
    heading_rad: float = 0.0
    min_range_m: float = 0.02
    max_range_m: float = 4.0
    source_map: str = ""


def _unique_cells(cells: Iterable[GridCell]) -> list[GridCell]:
    seen: set[GridCell] = set()
    ordered: list[GridCell] = []
    for cell in cells:
        if cell in seen:
            continue
        seen.add(cell)
        ordered.append(cell)
    return ordered


def project_polar_hit_to_cell(
    distance_m: float,
    angle_rad: float,
    *,
    origin_cell: GridCell,
    resolution_m: float,
) -> GridCell:
    if resolution_m <= 0:
        raise ValueError("resolution_m must be positive.")
    row_offset = int(round(-(distance_m * math.sin(angle_rad)) / resolution_m))
    col_offset = int(round((distance_m * math.cos(angle_rad)) / resolution_m))
    return (origin_cell[0] + row_offset, origin_cell[1] + col_offset)


def lidar_ranges_to_observation(
    ranges_m: Sequence[float],
    *,
    sequence_id: int,
    config: LidarProjectionConfig,
) -> SensorObservationMessage:
    projected_cells: List[GridCell] = []
    for index, distance_m in enumerate(ranges_m):
        if not math.isfinite(distance_m):
            continue
        if distance_m < config.min_range_m or distance_m > config.max_range_m:
            continue
        angle = config.angle_min_rad + index * config.angle_increment_rad
        projected_cells.append(
            project_polar_hit_to_cell(
                distance_m,
                angle,
                origin_cell=config.origin_cell,
                resolution_m=config.resolution_m,
            )
        )
    return SensorObservationMessage(
        sensor_type="lidar",
        detected_cells=_unique_cells(projected_cells),
        source_map=config.source_map,
        sequence_id=sequence_id,
    )


def ultrasonic_range_to_observation(
    distance_m: float,
    *,
    sequence_id: int,
    config: UltrasonicProjectionConfig,
) -> SensorObservationMessage:
    if not math.isfinite(distance_m):
        detected_cells: list[GridCell] = []
    elif config.min_range_m <= distance_m <= config.max_range_m:
        detected_cells = [
            project_polar_hit_to_cell(
                distance_m,
                config.heading_rad,
                origin_cell=config.origin_cell,
                resolution_m=config.resolution_m,
            )
        ]
    else:
        detected_cells = []
    return SensorObservationMessage(
        sensor_type="ultrasonic",
        detected_cells=detected_cells,
        source_map=config.source_map,
        sequence_id=sequence_id,
    )
