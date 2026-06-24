from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
src_root = repo_root / "ros2_ws" / "src"
for package_dir in src_root.iterdir():
    if package_dir.is_dir():
        sys.path.insert(0, str(package_dir))

from mapping.sensor_adapter_runtime import LidarAdapterRuntimeConfig, adapt_lidar_scan


class LidarAdapterRuntimeTests(unittest.TestCase):
    def test_adapt_lidar_scan_uses_frame_id_when_source_map_empty(self) -> None:
        observation = adapt_lidar_scan(
            [1.0],
            angle_min_rad=0.0,
            angle_increment_rad=0.1,
            sequence_id=4,
            config=LidarAdapterRuntimeConfig(
                origin_row=2,
                origin_col=2,
                resolution_m=1.0,
            ),
            frame_id="laser_frame",
        )

        self.assertEqual(observation.source_map, "laser_frame")
        self.assertEqual(observation.detected_cells, [(2, 3)])

    def test_adapt_lidar_scan_applies_stride(self) -> None:
        observation = adapt_lidar_scan(
            [1.0, 99.0, 1.0, 99.0],
            angle_min_rad=0.0,
            angle_increment_rad=math.pi / 2.0,
            sequence_id=1,
            config=LidarAdapterRuntimeConfig(
                origin_row=3,
                origin_col=3,
                resolution_m=1.0,
                max_range_m=4.0,
                scan_stride=2,
            ),
            frame_id="scan",
        )

        self.assertEqual(observation.detected_cells, [(3, 4), (3, 2)])

    def test_adapt_lidar_scan_applies_angle_offset(self) -> None:
        observation = adapt_lidar_scan(
            [1.0],
            angle_min_rad=0.0,
            angle_increment_rad=0.1,
            sequence_id=2,
            config=LidarAdapterRuntimeConfig(
                origin_row=5,
                origin_col=5,
                resolution_m=1.0,
                angle_offset_rad=math.pi / 2.0,
            ),
            frame_id="scan",
        )

        self.assertEqual(observation.detected_cells, [(4, 5)])


if __name__ == "__main__":
    unittest.main()
