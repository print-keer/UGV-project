from __future__ import annotations

from pathlib import Path

from autonomy_interfaces.contracts import MissionGoalMessage, NavigationStatusMessage, PlannerStatusMessage
from autonomy_interfaces.qos import build_topic_qos
from autonomy_interfaces.topic_transport import (
    decode_topic_message,
    encode_topic_message,
    get_topic_message_type,
    get_transport_mode,
)
from .topics import (
    MISSION_GOAL_PERIOD_SEC,
    MISSION_GOAL_TOPIC,
    NAVIGATION_STATUS_TOPIC,
    PLANNER_STATUS_TOPIC,
)


def main() -> None:
    try:
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import String
    except ImportError as exc:
        raise SystemExit(
            "rclpy and std_msgs are required to run mission_controller_node."
        ) from exc

    class MissionControllerNode(Node):
        def __init__(self) -> None:
            super().__init__("mission_controller_node")
            self.goal_message_type = get_topic_message_type(MISSION_GOAL_TOPIC, String)
            self.planner_status_type = get_topic_message_type(PLANNER_STATUS_TOPIC, String)
            self.navigation_status_type = get_topic_message_type(NAVIGATION_STATUS_TOPIC, String)
            self.goal = MissionGoalMessage(
                start_cell=(0, 0),
                goal_cell=(5, 5),
                goal_id="mission_demo_goal",
            )
            self.goal_publish_count = 0
            self.goal_publisher = self.create_publisher(
                self.goal_message_type,
                MISSION_GOAL_TOPIC,
                build_topic_qos(MISSION_GOAL_TOPIC),
            )
            self.create_subscription(
                self.planner_status_type,
                PLANNER_STATUS_TOPIC,
                self._on_planner_status,
                build_topic_qos(PLANNER_STATUS_TOPIC),
            )
            self.create_subscription(
                self.navigation_status_type,
                NAVIGATION_STATUS_TOPIC,
                self._on_navigation_status,
                build_topic_qos(NAVIGATION_STATUS_TOPIC),
            )
            self.create_timer(MISSION_GOAL_PERIOD_SEC, self._publish_goal)
            self.get_logger().info(
                f"Mission controller using {get_transport_mode()} transport for Person 1 topics."
            )
            self._publish_goal()

        def _publish_goal(self) -> None:
            repo_root = Path(__file__).resolve().parents[4]
            msg = encode_topic_message(MISSION_GOAL_TOPIC, self.goal, self.goal_message_type)
            self.goal_publisher.publish(msg)
            self.goal_publish_count += 1
            if self.goal_publish_count == 1 or self.goal_publish_count % 5 == 0:
                self.get_logger().info(
                    f"Published mission goal from {repo_root.name}: {self.goal}"
                )

        def _on_planner_status(self, msg) -> None:
            status = decode_topic_message(PLANNER_STATUS_TOPIC, msg)
            self.get_logger().info(
                f"Planner status goal_id={status.goal_id} state={status.state} visited={status.visited_nodes}"
            )

        def _on_navigation_status(self, msg) -> None:
            status = decode_topic_message(NAVIGATION_STATUS_TOPIC, msg)
            self.get_logger().info(
                f"Navigation status goal_id={status.goal_id} state={status.state} current={status.current_cell}"
            )

    rclpy.init()
    node = MissionControllerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
