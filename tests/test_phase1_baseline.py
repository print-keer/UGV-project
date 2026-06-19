from __future__ import annotations

import sys
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
src_root = repo_root / "ros2_ws" / "src"
for package_dir in src_root.iterdir():
    if package_dir.is_dir():
        sys.path.insert(0, str(package_dir))

from mission_controller.topics import MAP_PUBLISH_PERIOD_SEC, MAP_ROTATION_PERIOD_SEC, MISSION_GOAL_PERIOD_SEC


class Phase1BaselineTests(unittest.TestCase):
    def test_launch_file_exists(self) -> None:
        launch_path = (
            repo_root
            / "ros2_ws"
            / "src"
            / "mission_controller"
            / "launch"
            / "person1_stack.launch.py"
        )
        self.assertTrue(launch_path.exists())
        viz_launch_path = (
            repo_root
            / "ros2_ws"
            / "src"
            / "mission_controller"
            / "launch"
            / "person1_visualization.launch.py"
        )
        self.assertTrue(viz_launch_path.exists())
        observe_launch_path = (
            repo_root
            / "ros2_ws"
            / "src"
            / "mission_controller"
            / "launch"
            / "person1_observe.launch.py"
        )
        self.assertTrue(observe_launch_path.exists())
        rviz_config_path = (
            repo_root
            / "ros2_ws"
            / "src"
            / "mission_controller"
            / "rviz"
            / "person1_navigation.rviz"
        )
        self.assertTrue(rviz_config_path.exists())

    def test_phase1_periods_are_positive_and_consistent(self) -> None:
        self.assertGreater(MISSION_GOAL_PERIOD_SEC, 0.0)
        self.assertGreater(MAP_PUBLISH_PERIOD_SEC, 0.0)
        self.assertGreaterEqual(MAP_ROTATION_PERIOD_SEC, MAP_PUBLISH_PERIOD_SEC)


if __name__ == "__main__":
    unittest.main()
