from __future__ import annotations

import sys
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
src_root = repo_root / "ros2_ws" / "src"
for package_dir in src_root.iterdir():
    if package_dir.is_dir():
        sys.path.insert(0, str(package_dir))

from mapping.dynamic_world import DynamicWorld
from mapping.mock_maps import MockMap


class DynamicWorldTests(unittest.TestCase):
    def test_dynamic_world_advances_obstacle_sequence(self) -> None:
        mock_map = MockMap(
            name="dynamic_sequence",
            description="Sequence test map.",
            start=(0, 0),
            goal=(1, 3),
            grid=[
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            dynamic_obstacles=[(0, 1), (1, 2)],
        )

        world = DynamicWorld(mock_map)
        timeline = world.full_timeline()

        self.assertEqual(len(timeline), 3)
        self.assertEqual(timeline[0].occupancy_grid.revision, 0)
        self.assertEqual(timeline[1].applied_obstacle, (0, 1))
        self.assertEqual(timeline[2].applied_obstacle, (1, 2))
        self.assertTrue(timeline[-1].scenario_complete)


if __name__ == "__main__":
    unittest.main()
