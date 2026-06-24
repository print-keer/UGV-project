from __future__ import annotations

from dataclasses import dataclass

from .contracts import (
    MissionGoalMessage,
    MissionStateMessage,
    MotionCommandMessage,
    MotorStatusMessage,
    NavigationStatusMessage,
    OccupancyGridMessage,
    PlannedPathMessage,
    PlannerStatusMessage,
    ReplanRequestMessage,
    SensorObservationMessage,
)


@dataclass(frozen=True)
class RosMessageSupport:
    available: bool
    reason: str = ""


def get_ros_message_support() -> RosMessageSupport:
    try:
        from autonomy_msgs.msg import GridCell  # noqa: F401
    except ImportError as exc:
        return RosMessageSupport(
            available=False,
            reason=(
                "Typed ROS messages are not available in this environment. "
                "Build the ROS2 workspace so the generated autonomy_msgs package exists."
            ),
        )
    return RosMessageSupport(available=True)


def _require_ros_messages() -> None:
    support = get_ros_message_support()
    if not support.available:
        raise RuntimeError(support.reason)


def to_ros_occupancy_grid(message: OccupancyGridMessage):
    _require_ros_messages()
    from autonomy_msgs.msg import OccupancyGrid

    ros_msg = OccupancyGrid()
    ros_msg.width = message.width
    ros_msg.height = message.height
    ros_msg.resolution = float(message.resolution)
    ros_msg.origin_row = message.origin[0]
    ros_msg.origin_col = message.origin[1]
    ros_msg.data = list(message.data)
    ros_msg.frame_id = message.frame_id
    ros_msg.source_map = message.source_map
    ros_msg.revision = message.revision
    return ros_msg


def from_ros_occupancy_grid(message) -> OccupancyGridMessage:
    return OccupancyGridMessage(
        width=message.width,
        height=message.height,
        resolution=message.resolution,
        origin=(message.origin_row, message.origin_col),
        data=list(message.data),
        frame_id=message.frame_id,
        source_map=message.source_map,
        revision=message.revision,
    )


def to_ros_mission_goal(message: MissionGoalMessage):
    _require_ros_messages()
    from autonomy_msgs.msg import MissionGoal

    ros_msg = MissionGoal()
    ros_msg.goal_row = message.goal_cell[0]
    ros_msg.goal_col = message.goal_cell[1]
    ros_msg.has_start = message.start_cell is not None
    if message.start_cell is not None:
        ros_msg.start_row = message.start_cell[0]
        ros_msg.start_col = message.start_cell[1]
    ros_msg.goal_id = message.goal_id
    return ros_msg


def from_ros_mission_goal(message) -> MissionGoalMessage:
    start_cell = (message.start_row, message.start_col) if message.has_start else None
    return MissionGoalMessage(
        goal_cell=(message.goal_row, message.goal_col),
        start_cell=start_cell,
        goal_id=message.goal_id,
    )


def to_ros_planned_path(message: PlannedPathMessage):
    _require_ros_messages()
    from autonomy_msgs.msg import GridCell, PlannedPath

    ros_msg = PlannedPath()
    ros_msg.path_found = message.path_found
    ros_msg.total_cost = float(message.total_cost)
    ros_msg.goal_id = message.goal_id
    ros_msg.waypoints = [GridCell(row=row, col=col) for row, col in message.waypoints]
    return ros_msg


def from_ros_planned_path(message) -> PlannedPathMessage:
    return PlannedPathMessage(
        path_found=message.path_found,
        waypoints=[(cell.row, cell.col) for cell in message.waypoints],
        total_cost=message.total_cost,
        goal_id=message.goal_id,
    )


def to_ros_planner_status(message: PlannerStatusMessage):
    _require_ros_messages()
    from autonomy_msgs.msg import PlannerStatus

    ros_msg = PlannerStatus()
    ros_msg.state = message.state
    ros_msg.message = message.message
    ros_msg.goal_id = message.goal_id
    ros_msg.visited_nodes = message.visited_nodes
    ros_msg.has_start = message.start_cell is not None
    if message.start_cell is not None:
        ros_msg.start_row = message.start_cell[0]
        ros_msg.start_col = message.start_cell[1]
    ros_msg.has_goal = message.goal_cell is not None
    if message.goal_cell is not None:
        ros_msg.goal_row = message.goal_cell[0]
        ros_msg.goal_col = message.goal_cell[1]
    ros_msg.occupancy_revision = message.occupancy_revision
    return ros_msg


def from_ros_planner_status(message) -> PlannerStatusMessage:
    start_cell = (message.start_row, message.start_col) if message.has_start else None
    goal_cell = (message.goal_row, message.goal_col) if message.has_goal else None
    return PlannerStatusMessage(
        state=message.state,
        message=message.message,
        goal_id=message.goal_id,
        visited_nodes=message.visited_nodes,
        start_cell=start_cell,
        goal_cell=goal_cell,
        occupancy_revision=message.occupancy_revision,
    )


def to_ros_navigation_status(message: NavigationStatusMessage):
    _require_ros_messages()
    from autonomy_msgs.msg import NavigationStatus

    ros_msg = NavigationStatus()
    ros_msg.state = message.state
    ros_msg.message = message.message
    ros_msg.has_current_cell = message.current_cell is not None
    if message.current_cell is not None:
        ros_msg.current_row = message.current_cell[0]
        ros_msg.current_col = message.current_cell[1]
    ros_msg.current_waypoint_index = message.current_waypoint_index
    ros_msg.goal_id = message.goal_id
    ros_msg.path_length = message.path_length
    return ros_msg


def from_ros_navigation_status(message) -> NavigationStatusMessage:
    current_cell = (message.current_row, message.current_col) if message.has_current_cell else None
    return NavigationStatusMessage(
        state=message.state,
        message=message.message,
        current_cell=current_cell,
        current_waypoint_index=message.current_waypoint_index,
        goal_id=message.goal_id,
        path_length=message.path_length,
    )


def to_ros_replan_request(message: ReplanRequestMessage):
    _require_ros_messages()
    from autonomy_msgs.msg import ReplanRequest

    ros_msg = ReplanRequest()
    ros_msg.reason = message.reason
    ros_msg.has_current_cell = message.current_cell is not None
    if message.current_cell is not None:
        ros_msg.current_row = message.current_cell[0]
        ros_msg.current_col = message.current_cell[1]
    ros_msg.goal_id = message.goal_id
    ros_msg.occupancy_revision = message.occupancy_revision
    return ros_msg


def from_ros_replan_request(message) -> ReplanRequestMessage:
    current_cell = (message.current_row, message.current_col) if message.has_current_cell else None
    return ReplanRequestMessage(
        reason=message.reason,
        current_cell=current_cell,
        goal_id=message.goal_id,
        occupancy_revision=message.occupancy_revision,
    )


def to_ros_sensor_observation(message: SensorObservationMessage):
    _require_ros_messages()
    from autonomy_msgs.msg import GridCell, SensorObservation

    ros_msg = SensorObservation()
    ros_msg.sensor_type = message.sensor_type
    ros_msg.detected_cells = [GridCell(row=row, col=col) for row, col in message.detected_cells]
    ros_msg.source_map = message.source_map
    ros_msg.sequence_id = message.sequence_id
    return ros_msg


def from_ros_sensor_observation(message) -> SensorObservationMessage:
    return SensorObservationMessage(
        sensor_type=message.sensor_type,
        detected_cells=[(cell.row, cell.col) for cell in message.detected_cells],
        source_map=message.source_map,
        sequence_id=message.sequence_id,
    )


def to_ros_motion_command(message: MotionCommandMessage):
    _require_ros_messages()
    from autonomy_msgs.msg import MotionCommand

    ros_msg = MotionCommand()
    ros_msg.command_type = message.command_type
    ros_msg.has_target_cell = message.target_cell is not None
    if message.target_cell is not None:
        ros_msg.target_row = message.target_cell[0]
        ros_msg.target_col = message.target_cell[1]
    ros_msg.linear_velocity = float(message.linear_velocity)
    ros_msg.angular_velocity = float(message.angular_velocity)
    ros_msg.stop = message.stop
    ros_msg.goal_id = message.goal_id
    ros_msg.sequence_id = message.sequence_id
    return ros_msg


def from_ros_motion_command(message) -> MotionCommandMessage:
    target_cell = (message.target_row, message.target_col) if message.has_target_cell else None
    return MotionCommandMessage(
        command_type=message.command_type,
        target_cell=target_cell,
        linear_velocity=message.linear_velocity,
        angular_velocity=message.angular_velocity,
        stop=message.stop,
        goal_id=message.goal_id,
        sequence_id=message.sequence_id,
    )


def to_ros_motor_status(message: MotorStatusMessage):
    _require_ros_messages()
    from autonomy_msgs.msg import MotorStatus

    ros_msg = MotorStatus()
    ros_msg.state = message.state
    ros_msg.mode = message.mode
    ros_msg.applied = message.applied
    ros_msg.brake = message.brake
    ros_msg.emergency_stop = message.emergency_stop
    ros_msg.has_target_cell = message.target_cell is not None
    if message.target_cell is not None:
        ros_msg.target_row = message.target_cell[0]
        ros_msg.target_col = message.target_cell[1]
    ros_msg.applied_forward_speed = float(message.applied_forward_speed)
    ros_msg.applied_turn_rate = float(message.applied_turn_rate)
    ros_msg.left_wheel_speed = float(message.left_wheel_speed)
    ros_msg.right_wheel_speed = float(message.right_wheel_speed)
    ros_msg.goal_id = message.goal_id
    ros_msg.sequence_id = message.sequence_id
    ros_msg.detail = message.detail
    return ros_msg


def from_ros_motor_status(message) -> MotorStatusMessage:
    target_cell = (message.target_row, message.target_col) if message.has_target_cell else None
    return MotorStatusMessage(
        state=message.state,
        mode=message.mode,
        applied=message.applied,
        brake=message.brake,
        emergency_stop=message.emergency_stop,
        target_cell=target_cell,
        applied_forward_speed=message.applied_forward_speed,
        applied_turn_rate=message.applied_turn_rate,
        left_wheel_speed=message.left_wheel_speed,
        right_wheel_speed=message.right_wheel_speed,
        goal_id=message.goal_id,
        sequence_id=message.sequence_id,
        detail=message.detail,
    )


def to_ros_mission_state(message: MissionStateMessage):
    _require_ros_messages()
    from autonomy_msgs.msg import MissionState

    ros_msg = MissionState()
    ros_msg.state = message.state
    ros_msg.detail = message.detail
    ros_msg.goal_id = message.goal_id
    ros_msg.planner_state = message.planner_state
    ros_msg.navigation_state = message.navigation_state
    ros_msg.motor_mode = message.motor_mode
    ros_msg.motor_state = message.motor_state
    ros_msg.emergency_stop = message.emergency_stop
    return ros_msg


def from_ros_mission_state(message) -> MissionStateMessage:
    return MissionStateMessage(
        state=message.state,
        detail=message.detail,
        goal_id=message.goal_id,
        planner_state=message.planner_state,
        navigation_state=message.navigation_state,
        motor_mode=message.motor_mode,
        motor_state=message.motor_state,
        emergency_stop=message.emergency_stop,
    )
