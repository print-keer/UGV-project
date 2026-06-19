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

from mapping.sensor_projection import (  # noqa: E402
    LidarProjectionConfig,
    UltrasonicProjectionConfig,
    lidar_ranges_to_observation,
    project_polar_hit_to_cell,
    ultrasonic_range_to_observation,
)


class SensorProjectionTests(unittest.TestCase):
    def test_project_polar_hit_to_cell_projects_forward(self) -> None:
        self.assertEqual(
            project_polar_hit_to_cell(2.0, 0.0, origin_cell=(3, 4), resolution_m=1.0),
            (3, 6),
        )

    def test_project_polar_hit_to_cell_projects_left_with_negative_row(self) -> None:
        self.assertEqual(
            project_polar_hit_to_cell(2.0, math.pi / 2.0, origin_cell=(3, 4), resolution_m=1.0),
            (1, 4),
        )

    def test_lidar_ranges_to_observation_filters_invalid_ranges(self) -> None:
        observation = lidar_ranges_to_observation(
            [1.0, float("inf"), 9.0, 1.0],
            sequence_id=5,
            config=LidarProjectionConfig(
                origin_cell=(2, 2),
                resolution_m=1.0,
                angle_min_rad=0.0,
                angle_increment_rad=math.pi / 2.0,
                max_range_m=4.0,
                source_map="test_map",
            ),
        )

        self.assertEqual(observation.sensor_type, "lidar")
        self.assertEqual(observation.sequence_id, 5)
        self.assertEqual(observation.source_map, "test_map")
        self.assertEqual(observation.detected_cells, [(2, 3), (3, 2)])

    def test_ultrasonic_range_to_observation_projects_single_hit(self) -> None:
        observation = ultrasonic_range_to_observation(
            1.6,
            sequence_id=3,
            config=UltrasonicProjectionConfig(
                origin_cell=(4, 1),
                resolution_m=0.5,
                heading_rad=0.0,
                max_range_m=3.0,
                source_map="hardware",
            ),
        )

        self.assertEqual(observation.sensor_type, "ultrasonic")
        self.assertEqual(observation.detected_cells, [(4, 4)])

    def test_ultrasonic_range_to_observation_ignores_out_of_range_hits(self) -> None:
        observation = ultrasonic_range_to_observation(
            10.0,
            sequence_id=9,
            config=UltrasonicProjectionConfig(max_range_m=3.0),
        )

        self.assertEqual(observation.detected_cells, [])


if __name__ == "__main__":
    unittest.main()
