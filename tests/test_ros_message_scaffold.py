from __future__ import annotations

import sys
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
src_root = repo_root / "ros2_ws" / "src"
for package_dir in src_root.iterdir():
    if package_dir.is_dir():
        sys.path.insert(0, str(package_dir))

from autonomy_interfaces.ros_conversions import get_ros_message_support


class RosMessageScaffoldTests(unittest.TestCase):
    def test_autonomy_msgs_package_files_exist(self) -> None:
        package_root = repo_root / "ros2_ws" / "src" / "autonomy_msgs"

        self.assertTrue((package_root / "CMakeLists.txt").exists())
        self.assertTrue((package_root / "package.xml").exists())
        self.assertTrue((package_root / "msg" / "OccupancyGrid.msg").exists())
        self.assertTrue((package_root / "msg" / "MissionGoal.msg").exists())
        self.assertTrue((package_root / "msg" / "PlannedPath.msg").exists())
        self.assertTrue((package_root / "msg" / "PlannerStatus.msg").exists())
        self.assertTrue((package_root / "msg" / "NavigationStatus.msg").exists())
        self.assertTrue((package_root / "msg" / "ReplanRequest.msg").exists())
        self.assertTrue((package_root / "msg" / "SensorObservation.msg").exists())
        self.assertTrue((package_root / "msg" / "MotionCommand.msg").exists())
        self.assertTrue((package_root / "msg" / "MotorStatus.msg").exists())
        self.assertTrue((package_root / "msg" / "MissionState.msg").exists())

    def test_ros_message_support_check_is_safe_without_generated_msgs(self) -> None:
        support = get_ros_message_support()

        self.assertIsInstance(support.available, bool)
        if not support.available:
            self.assertIn("Build the ROS2 workspace", support.reason)


if __name__ == "__main__":
    unittest.main()
