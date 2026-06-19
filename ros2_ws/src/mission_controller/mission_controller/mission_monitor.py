from __future__ import annotations

from dataclasses import dataclass

from autonomy_interfaces.contracts import (
    MissionStateMessage,
    MotionCommandMessage,
    MotorStatusMessage,
    NavigationStatusMessage,
    PlannerStatusMessage,
)


@dataclass(frozen=True)
class MissionMonitorSnapshot:
    goal_id: str
    mission_state: str
    planner_state: str
    navigation_state: str
    motion_command_type: str
    motor_mode: str
    motor_state: str
    emergency_stop: bool


def build_monitor_snapshot(
    *,
    mission_state: MissionStateMessage | None = None,
    planner_status: PlannerStatusMessage | None = None,
    navigation_status: NavigationStatusMessage | None = None,
    motion_command: MotionCommandMessage | None = None,
    motor_status: MotorStatusMessage | None = None,
) -> MissionMonitorSnapshot:
    goal_id = (
        mission_state.goal_id
        if mission_state is not None
        else planner_status.goal_id
        if planner_status is not None
        else navigation_status.goal_id
        if navigation_status is not None
        else motion_command.goal_id
        if motion_command is not None
        else motor_status.goal_id
        if motor_status is not None
        else "default_goal"
    )
    return MissionMonitorSnapshot(
        goal_id=goal_id,
        mission_state=mission_state.state if mission_state is not None else "",
        planner_state=planner_status.state if planner_status is not None else "",
        navigation_state=navigation_status.state if navigation_status is not None else "",
        motion_command_type=motion_command.command_type if motion_command is not None else "",
        motor_mode=motor_status.mode if motor_status is not None else "",
        motor_state=motor_status.state if motor_status is not None else "",
        emergency_stop=motor_status.emergency_stop if motor_status is not None else False,
    )


def format_monitor_snapshot(snapshot: MissionMonitorSnapshot) -> str:
    return (
        f"goal={snapshot.goal_id} "
        f"mission={snapshot.mission_state or '-'} "
        f"planner={snapshot.planner_state or '-'} "
        f"navigation={snapshot.navigation_state or '-'} "
        f"motion={snapshot.motion_command_type or '-'} "
        f"motor={snapshot.motor_mode or '-'}:{snapshot.motor_state or '-'} "
        f"estop={snapshot.emergency_stop}"
    )
