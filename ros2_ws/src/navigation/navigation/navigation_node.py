from __future__ import annotations

from autonomy_interfaces.contracts import PlannedPathMessage
from autonomy_interfaces.qos import build_topic_qos
from autonomy_interfaces.topic_transport import (
    decode_topic_message,
    encode_topic_message,
    get_topic_message_type,
    get_transport_mode,
)
from mission_controller.topics import NAVIGATION_STATUS_TOPIC, PLANNED_PATH_TOPIC, REPLAN_REQUEST_TOPIC
from mission_controller.topics import MOTION_COMMAND_TOPIC

from .path_follower import PathFollower


def main() -> None:
    try:
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import String
    except ImportError as exc:
        raise SystemExit(
            "rclpy and std_msgs are required to run navigation_node."
        ) from exc

    class NavigationNode(Node):
        def __init__(self) -> None:
            super().__init__("navigation_node")
            self.follower = PathFollower()
            self.path_message_type = get_topic_message_type(PLANNED_PATH_TOPIC, String)
            self.status_message_type = get_topic_message_type(NAVIGATION_STATUS_TOPIC, String)
            self.replan_message_type = get_topic_message_type(REPLAN_REQUEST_TOPIC, String)
            self.motion_message_type = get_topic_message_type(MOTION_COMMAND_TOPIC, String)
            self.status_publisher = self.create_publisher(
                self.status_message_type,
                NAVIGATION_STATUS_TOPIC,
                build_topic_qos(NAVIGATION_STATUS_TOPIC),
            )
            self.replan_publisher = self.create_publisher(
                self.replan_message_type,
                REPLAN_REQUEST_TOPIC,
                build_topic_qos(REPLAN_REQUEST_TOPIC),
            )
            self.motion_publisher = self.create_publisher(
                self.motion_message_type,
                MOTION_COMMAND_TOPIC,
                build_topic_qos(MOTION_COMMAND_TOPIC),
            )
            self.create_subscription(
                self.path_message_type,
                PLANNED_PATH_TOPIC,
                self._on_path,
                build_topic_qos(PLANNED_PATH_TOPIC),
            )
            self.get_logger().info(
                f"Navigation node subscribed to planned paths using {get_transport_mode()} transport."
            )

        def _on_path(self, msg) -> None:
            planned_path = decode_topic_message(PLANNED_PATH_TOPIC, msg)
            execution = self.follower.follow_path(planned_path)
            report = execution.report

            status_msg = encode_topic_message(
                NAVIGATION_STATUS_TOPIC,
                report.status,
                self.status_message_type,
            )
            self.status_publisher.publish(status_msg)

            if report.replan_request is not None:
                replan_msg = encode_topic_message(
                    REPLAN_REQUEST_TOPIC,
                    report.replan_request,
                    self.replan_message_type,
                )
                self.replan_publisher.publish(replan_msg)

            for command in execution.motion_commands:
                motion_msg = encode_topic_message(
                    MOTION_COMMAND_TOPIC,
                    command,
                    self.motion_message_type,
                )
                self.motion_publisher.publish(motion_msg)

            self.get_logger().info(
                f"Navigation accepted={report.accepted} goal={planned_path.goal_id} "
                f"waypoints={report.waypoint_count} steps={len(execution.steps)} "
                f"motion_commands={len(execution.motion_commands)} "
                f"state={report.status.state}"
            )

    rclpy.init()
    node = NavigationNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
