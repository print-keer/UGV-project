from __future__ import annotations

import sys
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
src_root = repo_root / "ros2_ws" / "src"
for package_dir in src_root.iterdir():
    if package_dir.is_dir():
        sys.path.insert(0, str(package_dir))

from autonomy_interfaces.contracts import (
    MissionStateMessage,
    MotionCommandMessage,
    MotorStatusMessage,
    NavigationStatusMessage,
    PlannerStatusMessage,
)
from mission_controller.mission_monitor import build_monitor_snapshot, format_monitor_snapshot


class MissionMonitorTests(unittest.TestCase):
    def test_build_monitor_snapshot_collects_latest_statuses(self) -> None:
        snapshot = build_monitor_snapshot(
            mission_state=MissionStateMessage(
                state="navigating",
                detail="Mission active.",
                goal_id="goal_a",
            ),
            planner_status=PlannerStatusMessage(
                state="success",
                message="Path found.",
                goal_id="goal_a",
            ),
            navigation_status=NavigationStatusMessage(
                state="following_path",
                message="Following.",
                goal_id="goal_a",
            ),
            motion_command=MotionCommandMessage(
                command_type="step_to_cell",
                goal_id="goal_a",
            ),
            motor_status=MotorStatusMessage(
                state="applied",
                mode="track_cell",
                applied=True,
                brake=False,
                emergency_stop=False,
                goal_id="goal_a",
            ),
        )

        self.assertEqual(snapshot.goal_id, "goal_a")
        self.assertEqual(snapshot.mission_state, "navigating")
        self.assertEqual(snapshot.planner_state, "success")
        self.assertEqual(snapshot.navigation_state, "following_path")
        self.assertEqual(snapshot.motion_command_type, "step_to_cell")
        self.assertEqual(snapshot.motor_mode, "track_cell")
        self.assertEqual(snapshot.motor_state, "applied")

    def test_format_monitor_snapshot_is_human_readable(self) -> None:
        summary = format_monitor_snapshot(
            build_monitor_snapshot(
                mission_state=MissionStateMessage(
                    state="holding",
                    detail="Holding.",
                    goal_id="goal_b",
                ),
                motor_status=MotorStatusMessage(
                    state="applied",
                    mode="hold",
                    applied=True,
                    brake=True,
                    emergency_stop=False,
                    goal_id="goal_b",
                ),
            )
        )

        self.assertIn("goal=goal_b", summary)
        self.assertIn("mission=holding", summary)
        self.assertIn("motor=hold:applied", summary)


if __name__ == "__main__":
    unittest.main()
