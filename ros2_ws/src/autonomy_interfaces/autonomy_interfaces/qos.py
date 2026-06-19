from __future__ import annotations


def build_topic_qos(topic: str):
    try:
        from rclpy.qos import (
            DurabilityPolicy,
            HistoryPolicy,
            QoSProfile,
            ReliabilityPolicy,
        )
    except ImportError as exc:
        raise RuntimeError("rclpy is required to construct ROS2 QoS profiles.") from exc

    transient_topics = {
        "/mission/goal",
        "/mission/state",
        "/mapping/occupancy_grid",
        "/planner/path",
        "/planner/status",
        "/navigation/status",
    }

    durability = (
        DurabilityPolicy.TRANSIENT_LOCAL
        if topic in transient_topics
        else DurabilityPolicy.VOLATILE
    )

    return QoSProfile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=durability,
        history=HistoryPolicy.KEEP_LAST,
        depth=10,
    )
