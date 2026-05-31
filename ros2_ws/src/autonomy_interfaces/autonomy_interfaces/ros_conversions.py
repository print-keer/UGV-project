from __future__ import annotations

from dataclasses import dataclass

from .contracts import (
    MissionGoalMessage,
    NavigationStatusMessage,
    OccupancyGridMessage,
    PlannedPathMessage,
    PlannerStatusMessage,
    ReplanRequestMessage,
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
