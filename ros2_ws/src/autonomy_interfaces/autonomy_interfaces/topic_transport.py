from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Type

from mission_controller.topics import (
    MISSION_GOAL_TOPIC,
    NAVIGATION_STATUS_TOPIC,
    OCCUPANCY_GRID_TOPIC,
    PLANNED_PATH_TOPIC,
    PLANNER_STATUS_TOPIC,
    REPLAN_REQUEST_TOPIC,
)

from .contracts import (
    MissionGoalMessage,
    NavigationStatusMessage,
    OccupancyGridMessage,
    PlannedPathMessage,
    PlannerStatusMessage,
    ReplanRequestMessage,
)
from .ros_conversions import (
    from_ros_mission_goal,
    from_ros_navigation_status,
    from_ros_occupancy_grid,
    from_ros_planned_path,
    from_ros_planner_status,
    from_ros_replan_request,
    get_ros_message_support,
    to_ros_mission_goal,
    to_ros_navigation_status,
    to_ros_occupancy_grid,
    to_ros_planned_path,
    to_ros_planner_status,
    to_ros_replan_request,
)
from .serialization import deserialize_message, serialize_message


@dataclass(frozen=True)
class TopicSpec:
    dataclass_type: Type[Any]
    ros_type_name: str
    to_ros: Callable[[Any], Any]
    from_ros: Callable[[Any], Any]


TOPIC_SPECS = {
    OCCUPANCY_GRID_TOPIC: TopicSpec(
        dataclass_type=OccupancyGridMessage,
        ros_type_name="OccupancyGrid",
        to_ros=to_ros_occupancy_grid,
        from_ros=from_ros_occupancy_grid,
    ),
    MISSION_GOAL_TOPIC: TopicSpec(
        dataclass_type=MissionGoalMessage,
        ros_type_name="MissionGoal",
        to_ros=to_ros_mission_goal,
        from_ros=from_ros_mission_goal,
    ),
    PLANNED_PATH_TOPIC: TopicSpec(
        dataclass_type=PlannedPathMessage,
        ros_type_name="PlannedPath",
        to_ros=to_ros_planned_path,
        from_ros=from_ros_planned_path,
    ),
    PLANNER_STATUS_TOPIC: TopicSpec(
        dataclass_type=PlannerStatusMessage,
        ros_type_name="PlannerStatus",
        to_ros=to_ros_planner_status,
        from_ros=from_ros_planner_status,
    ),
    NAVIGATION_STATUS_TOPIC: TopicSpec(
        dataclass_type=NavigationStatusMessage,
        ros_type_name="NavigationStatus",
        to_ros=to_ros_navigation_status,
        from_ros=from_ros_navigation_status,
    ),
    REPLAN_REQUEST_TOPIC: TopicSpec(
        dataclass_type=ReplanRequestMessage,
        ros_type_name="ReplanRequest",
        to_ros=to_ros_replan_request,
        from_ros=from_ros_replan_request,
    ),
}


def get_transport_mode() -> str:
    return "typed" if get_ros_message_support().available else "string"


def get_topic_message_type(topic: str, string_cls: Type[Any]) -> Type[Any]:
    if get_ros_message_support().available:
        from autonomy_msgs import msg as autonomy_msg_module

        return getattr(autonomy_msg_module, TOPIC_SPECS[topic].ros_type_name)
    return string_cls


def encode_topic_message(topic: str, payload: Any, string_cls: Type[Any]) -> Any:
    spec = TOPIC_SPECS[topic]
    if get_ros_message_support().available:
        return spec.to_ros(payload)
    msg = string_cls()
    msg.data = serialize_message(payload)
    return msg


def decode_topic_message(topic: str, payload: Any) -> Any:
    spec = TOPIC_SPECS[topic]
    if get_ros_message_support().available:
        return spec.from_ros(payload)
    return deserialize_message(payload.data, spec.dataclass_type)

