from __future__ import annotations

from pathlib import Path

from autonomy_interfaces.topic_transport import (
    encode_topic_message,
    get_topic_message_type,
    get_transport_mode,
)
from autonomy_interfaces.qos import build_topic_qos
from mission_controller.topics import (
    MAP_PUBLISH_PERIOD_SEC,
    MAP_ROTATION_PERIOD_SEC,
    SIM_LIDAR_TOPIC,
    SIM_ULTRASONIC_TOPIC,
)

from .mock_maps import load_all_mock_maps
from .sensor_simulator import SensorScenario, SensorSimulator


def main() -> None:
    try:
        import rclpy
        from rclpy.node import Node
    except ImportError as exc:
        raise SystemExit(
            "rclpy is required to run sensor_simulator_node. Use the pure Python demo or install ROS2 Humble."
        ) from exc

    class SensorSimulatorNode(Node):
        def __init__(self) -> None:
            super().__init__("sensor_simulator_node")
            from std_msgs.msg import String

            repo_root = Path(__file__).resolve().parents[4]
            maps_dir = repo_root / "simulation" / "maps"
            self.maps = list(load_all_mock_maps(maps_dir).values())
            self.simulators = [SensorSimulator(mock_map) for mock_map in self.maps]
            self.scenario_indices = [0 for _ in self.maps]
            self.string_cls = String
            lidar_type = get_topic_message_type(SIM_LIDAR_TOPIC, self.string_cls)
            ultrasonic_type = get_topic_message_type(SIM_ULTRASONIC_TOPIC, self.string_cls)
            self.lidar_publisher = self.create_publisher(
                lidar_type,
                SIM_LIDAR_TOPIC,
                build_topic_qos(SIM_LIDAR_TOPIC),
            )
            self.ultrasonic_publisher = self.create_publisher(
                ultrasonic_type,
                SIM_ULTRASONIC_TOPIC,
                build_topic_qos(SIM_ULTRASONIC_TOPIC),
            )
            self.map_index = 0
            self.publish_count = 0
            self.create_timer(MAP_PUBLISH_PERIOD_SEC, self._publish_observations)
            self.get_logger().info(
                f"Sensor simulator node using {get_transport_mode()} transport on "
                f"{SIM_LIDAR_TOPIC} and {SIM_ULTRASONIC_TOPIC}."
            )

        def _publish_observations(self) -> None:
            if not self.maps:
                return
            mock_map = self.maps[self.map_index]
            scenario_index = self.scenario_indices[self.map_index]
            if scenario_index < max(
                len(mock_map.lidar_observations),
                len(mock_map.ultrasonic_observations),
            ):
                scenario = SensorScenario(
                    lidar_cells=(
                        list(mock_map.lidar_observations[scenario_index])
                        if scenario_index < len(mock_map.lidar_observations)
                        else []
                    ),
                    ultrasonic_cells=(
                        list(mock_map.ultrasonic_observations[scenario_index])
                        if scenario_index < len(mock_map.ultrasonic_observations)
                        else []
                    ),
                )
                observations = self.simulators[self.map_index].observe(scenario)
                for observation in observations:
                    if observation.sensor_type == "lidar":
                        self.lidar_publisher.publish(
                            encode_topic_message(
                                SIM_LIDAR_TOPIC,
                                observation,
                                self.string_cls,
                            )
                        )
                    elif observation.sensor_type == "ultrasonic":
                        self.ultrasonic_publisher.publish(
                            encode_topic_message(
                                SIM_ULTRASONIC_TOPIC,
                                observation,
                                self.string_cls,
                            )
                        )
                if observations:
                    self.get_logger().info(
                        f"Published simulated sensor observations map={mock_map.name} "
                        f"observations={[(obs.sensor_type, obs.detected_cells) for obs in observations]}"
                    )
                self.scenario_indices[self.map_index] += 1

            self.publish_count += 1
            if (
                len(self.maps) > 1
                and self.publish_count % int(MAP_ROTATION_PERIOD_SEC / MAP_PUBLISH_PERIOD_SEC) == 0
            ):
                self.map_index = (self.map_index + 1) % len(self.maps)
                self.scenario_indices[self.map_index] = 0
                self.simulators[self.map_index].sequence_id = 0

    rclpy.init()
    node = SensorSimulatorNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
