from __future__ import annotations

from dataclasses import dataclass

from autonomy_interfaces.contracts import (
    MissionGoalMessage,
    MissionStateMessage,
    REPLAN_NO_PATH_RECOVERY,
)
from .mission_state_machine import (
    MISSION_BLOCKED,
    MISSION_EMERGENCY_STOP,
    MISSION_GOAL_REACHED,
    MISSION_HOLDING,
)


MISSION_ACTION_REPUBLISH_GOAL = "republish_goal"
MISSION_ACTION_REQUEST_REPLAN = "request_replan"
MISSION_ACTION_HALT_MISSION = "halt_mission"


@dataclass(frozen=True)
class MissionAction:
    action_type: str
    detail: str
    reason: str = ""


class MissionPolicy:
    """Small action policy layered on top of mission-state updates."""

    def __init__(
        self,
        hold_republish_threshold: int = 2,
        blocked_replan_threshold: int = 2,
    ) -> None:
        self.hold_republish_threshold = hold_republish_threshold
        self.blocked_replan_threshold = blocked_replan_threshold
        self.hold_count = 0
        self.blocked_count = 0
        self.estop_latched = False
        self.mission_halted = False
        self.goal_reached = False

    def on_goal(self, goal: MissionGoalMessage) -> list[MissionAction]:
        del goal
        self.hold_count = 0
        self.blocked_count = 0
        self.goal_reached = False
        if not self.estop_latched:
            self.mission_halted = False
        return []

    def on_state(self, state: MissionStateMessage) -> list[MissionAction]:
        if self.estop_latched:
            return []

        actions: list[MissionAction] = []

        if state.state == MISSION_EMERGENCY_STOP:
            self.estop_latched = True
            self.mission_halted = True
            return [
                MissionAction(
                    action_type=MISSION_ACTION_HALT_MISSION,
                    detail="Emergency stop latched. Mission halted.",
                )
            ]

        if state.state == MISSION_GOAL_REACHED:
            self.goal_reached = True
            self.hold_count = 0
            self.blocked_count = 0
            return []

        if self.mission_halted or self.goal_reached:
            return []

        if state.state == MISSION_HOLDING:
            self.hold_count += 1
        else:
            self.hold_count = 0

        if state.state == MISSION_BLOCKED:
            self.blocked_count += 1
        else:
            self.blocked_count = 0

        if self.hold_count >= self.hold_republish_threshold:
            actions.append(
                MissionAction(
                    action_type=MISSION_ACTION_REPUBLISH_GOAL,
                    detail="Mission remained in holding state. Republishing goal.",
                )
            )
            self.hold_count = 0

        if self.blocked_count >= self.blocked_replan_threshold:
            actions.append(
                MissionAction(
                    action_type=MISSION_ACTION_REQUEST_REPLAN,
                    detail="Mission remained blocked. Requesting replanning.",
                    reason=REPLAN_NO_PATH_RECOVERY,
                )
            )
            self.blocked_count = 0

        return actions
