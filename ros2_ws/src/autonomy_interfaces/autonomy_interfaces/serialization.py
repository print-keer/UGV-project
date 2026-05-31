from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Type, TypeVar

from .contracts import (
    MissionGoalMessage,
    NavigationStatusMessage,
    OccupancyGridMessage,
    PlannedPathMessage,
    PlannerStatusMessage,
    ReplanRequestMessage,
)

T = TypeVar("T")


def serialize_message(message: object) -> str:
    return json.dumps(asdict(message))


def deserialize_message(payload: str, message_type: Type[T]) -> T:
    data = json.loads(payload)
    if message_type is OccupancyGridMessage:
        data["origin"] = tuple(data["origin"])
    if message_type is MissionGoalMessage:
        data["goal_cell"] = tuple(data["goal_cell"])
        if data.get("start_cell") is not None:
            data["start_cell"] = tuple(data["start_cell"])
    if message_type is PlannedPathMessage:
        data["waypoints"] = [tuple(item) for item in data["waypoints"]]
    if message_type is NavigationStatusMessage and data.get("current_cell") is not None:
        data["current_cell"] = tuple(data["current_cell"])
    if message_type is ReplanRequestMessage and data.get("current_cell") is not None:
        data["current_cell"] = tuple(data["current_cell"])
    if message_type is PlannerStatusMessage:
        if data.get("start_cell") is not None:
            data["start_cell"] = tuple(data["start_cell"])
        if data.get("goal_cell") is not None:
            data["goal_cell"] = tuple(data["goal_cell"])
    return message_type(**data)


def decode_for_topic(topic: str, payload: str) -> Any:
    topic_map = {
        "/mapping/occupancy_grid": OccupancyGridMessage,
        "/mission/goal": MissionGoalMessage,
        "/planner/path": PlannedPathMessage,
        "/planner/status": PlannerStatusMessage,
        "/navigation/status": NavigationStatusMessage,
        "/navigation/replan_request": ReplanRequestMessage,
    }
    message_type = topic_map[topic]
    return deserialize_message(payload, message_type)
