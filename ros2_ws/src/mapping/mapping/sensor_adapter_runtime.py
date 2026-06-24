from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from autonomy_interfaces.contracts import SensorObservationMessage

from .sensor_projection import LidarProjectionConfig, lidar_ranges_to_observation


@dataclass(frozen=True)
class LidarAdapterRuntimeConfig:
    origin_row: int = 0
    origin_col: int = 0
    resolution_m: float = 1.0
    min_range_m: float = 0.05
    max_range_m: float = 8.0
    scan_stride: int = 1
    angle_offset_rad: float = 0.0
    source_map: str = ""


def adapt_lidar_scan(
    ranges_m: Sequence[float],
    *,
    angle_min_rad: float,
    angle_increment_rad: float,
    sequence_id: int,
    config: LidarAdapterRuntimeConfig,
    frame_id: str = "",
) -> SensorObservationMessage:
    stride = max(1, int(config.scan_stride))
    filtered_ranges = list(ranges_m)[::stride]
    filtered_angle_increment = angle_increment_rad * stride
    projection_config = LidarProjectionConfig(
        origin_cell=(config.origin_row, config.origin_col),
        resolution_m=config.resolution_m,
        angle_min_rad=angle_min_rad + config.angle_offset_rad,
        angle_increment_rad=filtered_angle_increment,
        min_range_m=config.min_range_m,
        max_range_m=config.max_range_m,
        source_map=config.source_map or frame_id,
    )
    return lidar_ranges_to_observation(
        filtered_ranges,
        sequence_id=sequence_id,
        config=projection_config,
    )
