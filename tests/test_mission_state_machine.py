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
    MissionGoalMessage,
    MotorStatusMessage,
    NavigationStatusMessage,
    PlannerStatusMessage,
)
from mission_controller.mission_state_machine import (
    MISSION_BLOCKED,
    MISSION_EMERGENCY_STOP,
    MISSION_GOAL_REACHED,
    MISSION_HOLDING,
    MISSION_NAVIGATING,
    MISSION_PLANNING,
    MissionStateMachine,
)


class MissionStateMachineTests(unittest.TestCase):
    def test_goal_puts_machine_into_planning(self) -> None:
        machine = MissionStateMachine()
        state = machine.on_goal(MissionGoalMessage(goal_cell=(5, 5), start_cell=(0, 0), goal_id="goal_a"))
        self.assertEqual(state.state, MISSION_PLANNING)

    def test_planner_success_transitions_to_navigating(self) -> None:
        machine = MissionStateMachine()
        machine.on_goal(MissionGoalMessage(goal_cell=(1, 1), goal_id="goal_b"))
        state = machine.on_planner_status(
            PlannerStatusMessage(state="success", message="ok", goal_id="goal_b")
        )
        self.assertEqual(state.state, MISSION_NAVIGATING)

    def test_motor_hold_transitions_to_holding(self) -> None:
        machine = MissionStateMachine()
        machine.on_goal(MissionGoalMessage(goal_cell=(1, 1), goal_id="goal_c"))
        state = machine.on_motor_status(
            MotorStatusMessage(
                state="applied",
                mode="hold",
                applied=True,
                brake=True,
                emergency_stop=False,
                goal_id="goal_c",
            )
        )
        self.assertEqual(state.state, MISSION_HOLDING)

    def test_motor_estop_transitions_to_emergency_stop(self) -> None:
        machine = MissionStateMachine()
        machine.on_goal(MissionGoalMessage(goal_cell=(1, 1), goal_id="goal_d"))
        state = machine.on_motor_status(
            MotorStatusMessage(
                state="applied",
                mode="emergency_stop",
                applied=True,
                brake=True,
                emergency_stop=True,
                goal_id="goal_d",
            )
        )
        self.assertEqual(state.state, MISSION_EMERGENCY_STOP)
        self.assertTrue(state.emergency_stop)

    def test_navigation_blocked_transitions_to_blocked(self) -> None:
        machine = MissionStateMachine()
        machine.on_goal(MissionGoalMessage(goal_cell=(1, 1), goal_id="goal_e"))
        state = machine.on_navigation_status(
            NavigationStatusMessage(state="blocked", message="blocked", goal_id="goal_e")
        )
        self.assertEqual(state.state, MISSION_BLOCKED)

    def test_navigation_goal_reached_transitions_to_goal_reached(self) -> None:
        machine = MissionStateMachine()
        machine.on_goal(MissionGoalMessage(goal_cell=(1, 1), goal_id="goal_f"))
        state = machine.on_navigation_status(
            NavigationStatusMessage(state="reached_goal", message="done", goal_id="goal_f")
        )
        self.assertEqual(state.state, MISSION_GOAL_REACHED)


if __name__ == "__main__":
    unittest.main()
