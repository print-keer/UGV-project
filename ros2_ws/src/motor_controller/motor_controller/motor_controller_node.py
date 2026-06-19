from __future__ import annotations

from autonomy_interfaces.qos import build_topic_qos
from autonomy_interfaces.topic_transport import (
    decode_topic_message,
    encode_topic_message,
    get_topic_message_type,
    get_transport_mode,
)
from mission_controller.topics import MOTOR_STATUS_TOPIC, MOTION_COMMAND_TOPIC
from navigation.motion_adapter import to_motor_control_command

from .driver_stub import MotorDriverStub


def main() -> None:
    try:
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import String
    except ImportError as exc:
        raise SystemExit(
            "rclpy and std_msgs are required to run motor_controller_node."
        ) from exc

    class MotorControllerNode(Node):
        def __init__(self) -> None:
            super().__init__("motor_controller_node")
            self.driver = MotorDriverStub()
            self.command_message_type = get_topic_message_type(MOTION_COMMAND_TOPIC, String)
            self.status_message_type = get_topic_message_type(MOTOR_STATUS_TOPIC, String)
            self.status_publisher = self.create_publisher(
                self.status_message_type,
                MOTOR_STATUS_TOPIC,
                build_topic_qos(MOTOR_STATUS_TOPIC),
            )
            self.create_subscription(
                self.command_message_type,
                MOTION_COMMAND_TOPIC,
                self._on_command,
                build_topic_qos(MOTION_COMMAND_TOPIC),
            )
            self.get_logger().info(
                f"Motor controller stub subscribed to {MOTION_COMMAND_TOPIC} and publishing "
                f"{MOTOR_STATUS_TOPIC} using {get_transport_mode()} transport."
            )

        def _on_command(self, msg) -> None:
            command = decode_topic_message(MOTION_COMMAND_TOPIC, msg)
            motor_command = to_motor_control_command(command)
            status = self.driver.apply(motor_command)
            self.status_publisher.publish(
                encode_topic_message(MOTOR_STATUS_TOPIC, status, self.status_message_type)
            )
            self.get_logger().info(
                f"Applied motor mode={status.mode} target={status.target_cell} "
                f"speed={status.applied_forward_speed:.2f} turn={status.applied_turn_rate:.2f} "
                f"left={status.left_wheel_speed:.2f} right={status.right_wheel_speed:.2f} "
                f"brake={status.brake} estop={status.emergency_stop}"
            )

    rclpy.init()
    node = MotorControllerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
