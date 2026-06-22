from __future__ import annotations

import sys
from pathlib import Path


def _add_repo_root_to_path() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    sys.path.insert(0, str(repo_root))


def main() -> None:
    try:
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import String
    except ImportError as exc:
        raise SystemExit(
            "rclpy is required to run alert_node. Use the pure Python threat classifier modules or install ROS2 Humble."
        ) from exc

    _add_repo_root_to_path()

    from ai.threat_classifier.classifier import assess_detections
    from ai.threat_classifier.contracts import (
        deserialize_detection_result,
        serialize_assessment,
    )

    class AlertNode(Node):
        def __init__(self) -> None:
            super().__init__("alert_node")
            self.alert_publisher = self.create_publisher(String, "threat_detection/alerts", 10)
            self.create_subscription(
                String,
                "vision/detections",
                self._handle_detection_message,
                10,
            )
            self.get_logger().info(
                "Threat detection node scaffold is ready for detection messages on vision/detections."
            )

        def _handle_detection_message(self, message: String) -> None:
            result = deserialize_detection_result(message.data)
            assessment = assess_detections(result.detections)
            alert_message = String()
            alert_message.data = serialize_assessment(result.frame_id, assessment)
            self.alert_publisher.publish(alert_message)
            self.get_logger().info(f"{result.frame_id}: {assessment.summary}")

    rclpy.init()
    node = AlertNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
