from __future__ import annotations

import sys
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
src_root = repo_root / "ros2_ws" / "src"
for package_dir in src_root.iterdir():
    if package_dir.is_dir():
        sys.path.insert(0, str(package_dir))

from motor_controller.driver_stub import MotorDriverStub
from navigation.motion_adapter import MotorControlCommand


class MotorControllerTests(unittest.TestCase):
    def test_driver_stub_applies_track_cell_command(self) -> None:
        driver = MotorDriverStub()
        status = driver.apply(
            MotorControlCommand(
                mode="track_cell",
                target_row=3,
                target_col=4,
                forward_speed=0.5,
                turn_rate=0.1,
                left_wheel_speed=0.48,
                right_wheel_speed=0.52,
                brake=False,
                emergency_stop=False,
                goal_id="goal_a",
                sequence_id=1,
            )
        )

        self.assertTrue(status.applied)
        self.assertEqual(status.mode, "track_cell")
        self.assertEqual(status.target_cell, (3, 4))
        self.assertEqual(status.applied_forward_speed, 0.5)
        self.assertEqual(status.applied_turn_rate, 0.1)
        self.assertEqual(status.left_wheel_speed, 0.48)
        self.assertEqual(status.right_wheel_speed, 0.52)

    def test_driver_stub_applies_emergency_stop(self) -> None:
        driver = MotorDriverStub()
        status = driver.apply(
            MotorControlCommand(
                mode="emergency_stop",
                target_row=None,
                target_col=None,
                forward_speed=0.0,
                turn_rate=0.0,
                left_wheel_speed=0.0,
                right_wheel_speed=0.0,
                brake=True,
                emergency_stop=True,
                goal_id="goal_b",
                sequence_id=2,
            )
        )

        self.assertTrue(status.brake)
        self.assertTrue(status.emergency_stop)
        self.assertEqual(status.mode, "emergency_stop")


if __name__ == "__main__":
    unittest.main()
