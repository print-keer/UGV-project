from __future__ import annotations

from autonomy_interfaces.qos import build_topic_qos
from autonomy_interfaces.topic_transport import (
    decode_topic_message,
    get_topic_message_type,
    get_transport_mode,
)
from .mission_monitor import build_monitor_snapshot, format_monitor_snapshot
from .topics import (
    MISSION_STATE_TOPIC,
    MOTOR_STATUS_TOPIC,
    MOTION_COMMAND_TOPIC,
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
            "rclpy and std_msgs are required to run monitor_node."
        ) from exc

    class MissionMonitorNode(Node):
        def __init__(self) -> None:
            super().__init__("mission_monitor_node")
            self.planner_status = None
            self.navigation_status = None
            self.motion_command = None
            self.motor_status = None
            self.mission_state = None

            self.planner_type = get_topic_message_type(PLANNER_STATUS_TOPIC, String)
            self.navigation_type = get_topic_message_type(NAVIGATION_STATUS_TOPIC, String)
            self.motion_type = get_topic_message_type(MOTION_COMMAND_TOPIC, String)
            self.motor_type = get_topic_message_type(MOTOR_STATUS_TOPIC, String)
            self.mission_state_type = get_topic_message_type(MISSION_STATE_TOPIC, String)

            self.create_subscription(
                self.planner_type,
                PLANNER_STATUS_TOPIC,
                self._on_planner_status,
                build_topic_qos(PLANNER_STATUS_TOPIC),
            )
            self.create_subscription(
                self.navigation_type,
                NAVIGATION_STATUS_TOPIC,
                self._on_navigation_status,
                build_topic_qos(NAVIGATION_STATUS_TOPIC),
            )
            self.create_subscription(
                self.motion_type,
                MOTION_COMMAND_TOPIC,
                self._on_motion_command,
                build_topic_qos(MOTION_COMMAND_TOPIC),
            )
            self.create_subscription(
                self.motor_type,
                MOTOR_STATUS_TOPIC,
                self._on_motor_status,
                build_topic_qos(MOTOR_STATUS_TOPIC),
            )
            self.create_subscription(
                self.mission_state_type,
                MISSION_STATE_TOPIC,
                self._on_mission_state,
                build_topic_qos(MISSION_STATE_TOPIC),
            )
            self.create_timer(2.0, self._log_snapshot)
            self.get_logger().info(
                f"Mission monitor node observing Person 1 topics using {get_transport_mode()} transport."
            )

        def _on_planner_status(self, msg) -> None:
            self.planner_status = decode_topic_message(PLANNER_STATUS_TOPIC, msg)

        def _on_navigation_status(self, msg) -> None:
            self.navigation_status = decode_topic_message(NAVIGATION_STATUS_TOPIC, msg)

        def _on_motion_command(self, msg) -> None:
            self.motion_command = decode_topic_message(MOTION_COMMAND_TOPIC, msg)

        def _on_motor_status(self, msg) -> None:
            self.motor_status = decode_topic_message(MOTOR_STATUS_TOPIC, msg)

        def _on_mission_state(self, msg) -> None:
            self.mission_state = decode_topic_message(MISSION_STATE_TOPIC, msg)

        def _log_snapshot(self) -> None:
            snapshot = build_monitor_snapshot(
                mission_state=self.mission_state,
                planner_status=self.planner_status,
                navigation_status=self.navigation_status,
                motion_command=self.motion_command,
                motor_status=self.motor_status,
            )
            self.get_logger().info(f"Monitor snapshot: {format_monitor_snapshot(snapshot)}")

    rclpy.init()
    node = MissionMonitorNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
