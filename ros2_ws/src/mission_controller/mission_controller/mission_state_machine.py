from __future__ import annotations

from autonomy_interfaces.contracts import (
    MissionGoalMessage,
    MissionStateMessage,
    MotorStatusMessage,
    NavigationStatusMessage,
    PlannerStatusMessage,
)

MISSION_AWAITING_GOAL = "awaiting_goal"
MISSION_PLANNING = "planning"
MISSION_NAVIGATING = "navigating"
MISSION_HOLDING = "holding"
MISSION_BLOCKED = "blocked"
MISSION_EMERGENCY_STOP = "emergency_stop"
MISSION_GOAL_REACHED = "goal_reached"


class MissionStateMachine:
    def __init__(self) -> None:
        self.goal: MissionGoalMessage | None = None
        self.last_planner_status: PlannerStatusMessage | None = None
        self.last_navigation_status: NavigationStatusMessage | None = None
        self.last_motor_status: MotorStatusMessage | None = None
        self.current_state = MISSION_AWAITING_GOAL

    def _build_state(self, detail: str) -> MissionStateMessage:
        goal_id = self.goal.goal_id if self.goal is not None else "default_goal"
        return MissionStateMessage(
            state=self.current_state,
            detail=detail,
            goal_id=goal_id,
            planner_state=self.last_planner_status.state if self.last_planner_status else "",
            navigation_state=self.last_navigation_status.state if self.last_navigation_status else "",
            motor_mode=self.last_motor_status.mode if self.last_motor_status else "",
            motor_state=self.last_motor_status.state if self.last_motor_status else "",
            emergency_stop=self.last_motor_status.emergency_stop if self.last_motor_status else False,
        )

    def on_goal(self, goal: MissionGoalMessage) -> MissionStateMessage:
        self.goal = goal
        self.current_state = MISSION_PLANNING
        return self._build_state("Mission goal received. Planning started.")

    def on_planner_status(self, status: PlannerStatusMessage) -> MissionStateMessage:
        self.last_planner_status = status
        if status.state == "success":
            self.current_state = MISSION_NAVIGATING
            return self._build_state("Planner found a route. Navigation may proceed.")
        if status.state == "no_path":
            self.current_state = MISSION_BLOCKED
            return self._build_state("Planner reported no path.")
        if status.state == "planning":
            self.current_state = MISSION_PLANNING
            return self._build_state("Planner is computing a route.")
        return self._build_state(f"Planner reported state={status.state}.")

    def on_navigation_status(self, status: NavigationStatusMessage) -> MissionStateMessage:
        self.last_navigation_status = status
        if status.state == "reached_goal":
            self.current_state = MISSION_GOAL_REACHED
            return self._build_state("Navigation reached the goal.")
        if status.state == "blocked":
            self.current_state = MISSION_BLOCKED
            return self._build_state("Navigation reported a blocked route.")
        if status.state == "following_path":
            self.current_state = MISSION_NAVIGATING
            return self._build_state("Navigation is following the planned path.")
        return self._build_state(f"Navigation reported state={status.state}.")

    def on_motor_status(self, status: MotorStatusMessage) -> MissionStateMessage:
        self.last_motor_status = status
        if status.emergency_stop:
            self.current_state = MISSION_EMERGENCY_STOP
            return self._build_state("Motor layer triggered emergency stop.")
        if status.mode == "hold":
            self.current_state = MISSION_HOLDING
            return self._build_state("Motor layer is holding position.")
        if status.mode == "track_cell" and status.applied:
            self.current_state = MISSION_NAVIGATING
            return self._build_state("Motor layer accepted movement command.")
        return self._build_state(f"Motor layer reported mode={status.mode}.")
