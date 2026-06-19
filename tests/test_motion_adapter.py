from __future__ import annotations

import sys
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
src_root = repo_root / "ros2_ws" / "src"
for package_dir in src_root.iterdir():
    if package_dir.is_dir():
        sys.path.insert(0, str(package_dir))

from autonomy_interfaces.contracts import MotionCommandMessage
from navigation.motion_adapter import DifferentialDriveConfig, differential_drive_wheel_speeds, to_motor_control_command


class MotionAdapterTests(unittest.TestCase):
    def test_step_command_maps_to_track_cell_mode(self) -> None:
        motor_command = to_motor_control_command(
            MotionCommandMessage(
                command_type="step_to_cell",
                target_cell=(2, 3),
                linear_velocity=0.6,
                angular_velocity=0.1,
                stop=False,
                goal_id="goal_a",
                sequence_id=1,
            )
        )

        self.assertEqual(motor_command.mode, "track_cell")
        self.assertEqual((motor_command.target_row, motor_command.target_col), (2, 3))
        self.assertEqual(motor_command.forward_speed, 0.6)
        self.assertEqual(motor_command.turn_rate, 0.1)
        self.assertAlmostEqual(motor_command.left_wheel_speed, 0.58)
        self.assertAlmostEqual(motor_command.right_wheel_speed, 0.62)
        self.assertFalse(motor_command.brake)
        self.assertFalse(motor_command.emergency_stop)

    def test_hold_position_maps_to_hold_mode(self) -> None:
        motor_command = to_motor_control_command(
            MotionCommandMessage(
                command_type="hold_position",
                target_cell=None,
                linear_velocity=0.0,
                angular_velocity=0.0,
                stop=True,
                goal_id="goal_b",
                sequence_id=2,
            )
        )

        self.assertEqual(motor_command.mode, "hold")
        self.assertTrue(motor_command.brake)
        self.assertFalse(motor_command.emergency_stop)

    def test_emergency_stop_maps_to_estop_mode(self) -> None:
        motor_command = to_motor_control_command(
            MotionCommandMessage(
                command_type="emergency_stop",
                target_cell=(1, 1),
                linear_velocity=0.5,
                angular_velocity=0.3,
                stop=True,
                goal_id="goal_c",
                sequence_id=3,
            )
        )

        self.assertEqual(motor_command.mode, "emergency_stop")
        self.assertEqual(motor_command.forward_speed, 0.0)
        self.assertEqual(motor_command.turn_rate, 0.0)
        self.assertEqual(motor_command.left_wheel_speed, 0.0)
        self.assertEqual(motor_command.right_wheel_speed, 0.0)
        self.assertTrue(motor_command.brake)
        self.assertTrue(motor_command.emergency_stop)

    def test_differential_drive_wheel_speeds_are_clamped(self) -> None:
        left, right = differential_drive_wheel_speeds(
            1.5,
            1.0,
            DifferentialDriveConfig(track_width_m=0.5, max_wheel_speed=1.0),
        )

        self.assertEqual(left, 1.0)
        self.assertEqual(right, 1.0)


if __name__ == "__main__":
    unittest.main()
