from __future__ import annotations

import sys
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
src_root = repo_root / "ros2_ws" / "src"
for package_dir in src_root.iterdir():
    if package_dir.is_dir():
        sys.path.insert(0, str(package_dir))

from autonomy_interfaces.contracts import MissionGoalMessage, MissionStateMessage
from mission_controller.mission_policy import (
    MISSION_ACTION_HALT_MISSION,
    MISSION_ACTION_REPUBLISH_GOAL,
    MISSION_ACTION_REQUEST_REPLAN,
    MissionPolicy,
)


class MissionPolicyTests(unittest.TestCase):
    def test_hold_state_triggers_goal_republish_after_threshold(self) -> None:
        policy = MissionPolicy(hold_republish_threshold=2)
        policy.on_goal(MissionGoalMessage(goal_cell=(1, 1), goal_id="goal_a"))

        self.assertEqual(
            policy.on_state(MissionStateMessage(state="holding", detail="hold", goal_id="goal_a")),
            [],
        )
        actions = policy.on_state(MissionStateMessage(state="holding", detail="hold", goal_id="goal_a"))

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].action_type, MISSION_ACTION_REPUBLISH_GOAL)

    def test_blocked_state_triggers_replan_after_threshold(self) -> None:
        policy = MissionPolicy(blocked_replan_threshold=2)
        policy.on_goal(MissionGoalMessage(goal_cell=(1, 1), goal_id="goal_b"))

        self.assertEqual(
            policy.on_state(MissionStateMessage(state="blocked", detail="blocked", goal_id="goal_b")),
            [],
        )
        actions = policy.on_state(MissionStateMessage(state="blocked", detail="blocked", goal_id="goal_b"))

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].action_type, MISSION_ACTION_REQUEST_REPLAN)

    def test_emergency_stop_halts_mission(self) -> None:
        policy = MissionPolicy()
        policy.on_goal(MissionGoalMessage(goal_cell=(1, 1), goal_id="goal_c"))
        actions = policy.on_state(
            MissionStateMessage(
                state="emergency_stop",
                detail="estop",
                goal_id="goal_c",
                emergency_stop=True,
            )
        )

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].action_type, MISSION_ACTION_HALT_MISSION)
        self.assertTrue(policy.mission_halted)


if __name__ == "__main__":
    unittest.main()
