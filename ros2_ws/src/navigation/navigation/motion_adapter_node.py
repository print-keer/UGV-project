from __future__ import annotations

from autonomy_interfaces.topic_transport import (
    decode_topic_message,
    get_topic_message_type,
    get_transport_mode,
)
from autonomy_interfaces.qos import build_topic_qos
from mission_controller.topics import MOTION_COMMAND_TOPIC

from .motion_adapter import to_motor_control_command


def main() -> None:
    try:
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import String
    except ImportError as exc:
        raise SystemExit(
            "rclpy and std_msgs are required to run motion_adapter_node."
        ) from exc

    class MotionAdapterNode(Node):
        def __init__(self) -> None:
            super().__init__("motion_adapter_node")
            self.command_message_type = get_topic_message_type(MOTION_COMMAND_TOPIC, String)
            self.create_subscription(
                self.command_message_type,
                MOTION_COMMAND_TOPIC,
                self._on_command,
                build_topic_qos(MOTION_COMMAND_TOPIC),
            )
            self.get_logger().info(
                f"Motion adapter node subscribed to {MOTION_COMMAND_TOPIC} using "
                f"{get_transport_mode()} transport."
            )

        def _on_command(self, msg) -> None:
            command = decode_topic_message(MOTION_COMMAND_TOPIC, msg)
            motor_command = to_motor_control_command(command)
            self.get_logger().info(
                f"Motor API preview mode={motor_command.mode} "
                f"target=({motor_command.target_row}, {motor_command.target_col}) "
                f"speed={motor_command.forward_speed:.2f} turn={motor_command.turn_rate:.2f} "
                f"left={motor_command.left_wheel_speed:.2f} right={motor_command.right_wheel_speed:.2f} "
                f"brake={motor_command.brake} estop={motor_command.emergency_stop} "
                f"goal={motor_command.goal_id} sequence={motor_command.sequence_id}"
            )

    rclpy.init()
    node = MotionAdapterNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
