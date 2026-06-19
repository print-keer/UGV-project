from __future__ import annotations

from autonomy_interfaces.qos import build_topic_qos
from autonomy_interfaces.topic_transport import (
    encode_topic_message,
    get_topic_message_type,
    get_transport_mode,
)
from mission_controller.topics import SIM_LIDAR_TOPIC, SIM_ULTRASONIC_TOPIC

from .sensor_projection import (
    LidarProjectionConfig,
    UltrasonicProjectionConfig,
    lidar_ranges_to_observation,
    ultrasonic_range_to_observation,
)


def lidar_adapter_main() -> None:
    try:
        import rclpy
        from rclpy.node import Node
        from sensor_msgs.msg import LaserScan
    except ImportError as exc:
        raise SystemExit(
            "rclpy and sensor_msgs are required to run lidar_adapter_node."
        ) from exc

    class LidarAdapterNode(Node):
        def __init__(self) -> None:
            super().__init__("lidar_adapter_node")
            from std_msgs.msg import String

            self.declare_parameter("input_topic", "/scan")
            self.declare_parameter("output_topic", SIM_LIDAR_TOPIC)
            self.declare_parameter("origin_row", 0)
            self.declare_parameter("origin_col", 0)
            self.declare_parameter("resolution_m", 1.0)
            self.declare_parameter("min_range_m", 0.05)
            self.declare_parameter("max_range_m", 8.0)
            self.declare_parameter("source_map", "")

            input_topic = str(self.get_parameter("input_topic").value)
            self.output_topic = str(self.get_parameter("output_topic").value)
            self.string_cls = String
            self.output_message_type = get_topic_message_type(self.output_topic, self.string_cls)
            self.publisher = self.create_publisher(
                self.output_message_type,
                self.output_topic,
                build_topic_qos(self.output_topic),
            )
            self.sequence_id = 0
            self.create_subscription(LaserScan, input_topic, self._on_scan, 10)
            self.get_logger().info(
                f"Lidar adapter consuming {input_topic} and publishing {self.output_topic} "
                f"using {get_transport_mode()} transport."
            )

        def _on_scan(self, msg: "LaserScan") -> None:
            configured_max = float(self.get_parameter("max_range_m").value)
            config = LidarProjectionConfig(
                origin_cell=(
                    int(self.get_parameter("origin_row").value),
                    int(self.get_parameter("origin_col").value),
                ),
                resolution_m=float(self.get_parameter("resolution_m").value),
                angle_min_rad=float(msg.angle_min),
                angle_increment_rad=float(msg.angle_increment),
                min_range_m=float(self.get_parameter("min_range_m").value),
                max_range_m=min(configured_max, float(msg.range_max) if msg.range_max > 0 else configured_max),
                source_map=str(self.get_parameter("source_map").value),
            )
            observation = lidar_ranges_to_observation(
                list(msg.ranges),
                sequence_id=self.sequence_id,
                config=config,
            )
            self.publisher.publish(
                encode_topic_message(self.output_topic, observation, self.string_cls)
            )
            self.sequence_id += 1

    rclpy.init()
    node = LidarAdapterNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


def ultrasonic_adapter_main() -> None:
    try:
        import rclpy
        from rclpy.node import Node
        from sensor_msgs.msg import Range
    except ImportError as exc:
        raise SystemExit(
            "rclpy and sensor_msgs are required to run ultrasonic_adapter_node."
        ) from exc

    class UltrasonicAdapterNode(Node):
        def __init__(self) -> None:
            super().__init__("ultrasonic_adapter_node")
            from std_msgs.msg import String

            self.declare_parameter("input_topic", "/ultrasonic/range")
            self.declare_parameter("output_topic", SIM_ULTRASONIC_TOPIC)
            self.declare_parameter("origin_row", 0)
            self.declare_parameter("origin_col", 0)
            self.declare_parameter("resolution_m", 1.0)
            self.declare_parameter("heading_rad", 0.0)
            self.declare_parameter("min_range_m", 0.02)
            self.declare_parameter("max_range_m", 4.0)
            self.declare_parameter("source_map", "")

            input_topic = str(self.get_parameter("input_topic").value)
            self.output_topic = str(self.get_parameter("output_topic").value)
            self.string_cls = String
            self.output_message_type = get_topic_message_type(self.output_topic, self.string_cls)
            self.publisher = self.create_publisher(
                self.output_message_type,
                self.output_topic,
                build_topic_qos(self.output_topic),
            )
            self.sequence_id = 0
            self.create_subscription(Range, input_topic, self._on_range, 10)
            self.get_logger().info(
                f"Ultrasonic adapter consuming {input_topic} and publishing {self.output_topic} "
                f"using {get_transport_mode()} transport."
            )

        def _on_range(self, msg: "Range") -> None:
            configured_max = float(self.get_parameter("max_range_m").value)
            config = UltrasonicProjectionConfig(
                origin_cell=(
                    int(self.get_parameter("origin_row").value),
                    int(self.get_parameter("origin_col").value),
                ),
                resolution_m=float(self.get_parameter("resolution_m").value),
                heading_rad=float(self.get_parameter("heading_rad").value),
                min_range_m=max(float(self.get_parameter("min_range_m").value), float(msg.min_range)),
                max_range_m=min(configured_max, float(msg.max_range) if msg.max_range > 0 else configured_max),
                source_map=str(self.get_parameter("source_map").value),
            )
            observation = ultrasonic_range_to_observation(
                float(msg.range),
                sequence_id=self.sequence_id,
                config=config,
            )
            self.publisher.publish(
                encode_topic_message(self.output_topic, observation, self.string_cls)
            )
            self.sequence_id += 1

    rclpy.init()
    node = UltrasonicAdapterNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
