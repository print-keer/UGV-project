from __future__ import annotations

from pathlib import Path

from autonomy_interfaces.qos import build_topic_qos
from autonomy_interfaces.topic_transport import (
    decode_topic_message,
    encode_topic_message,
    get_topic_message_type,
    get_transport_mode,
)
from mission_controller.topics import (
    MAP_PUBLISH_PERIOD_SEC,
    MAP_ROTATION_PERIOD_SEC,
    OCCUPANCY_GRID_TOPIC,
    SIM_LIDAR_TOPIC,
    SIM_ULTRASONIC_TOPIC,
)
from .dynamic_world import DynamicWorld

from .map_provider import MapProvider
from .mock_maps import load_all_mock_maps


def main() -> None:
    try:
        import rclpy
        from rclpy.node import Node
    except ImportError as exc:
        raise SystemExit(
            "rclpy is required to run mock_map_node. Use the pure Python demo or install ROS2 Humble."
        ) from exc

    class MockMapNode(Node):
        def __init__(self) -> None:
            super().__init__("mock_map_node")
            from std_msgs.msg import String

            repo_root = Path(__file__).resolve().parents[4]
            maps_dir = repo_root / "simulation" / "maps"
            provider = MapProvider()
            self.maps = list(load_all_mock_maps(maps_dir).values())
            self.provider = provider
            self.worlds = [DynamicWorld(mock_map, provider) for mock_map in self.maps]
            self.message_type = get_topic_message_type(OCCUPANCY_GRID_TOPIC, String)
            self.sensor_message_type = get_topic_message_type(SIM_LIDAR_TOPIC, String)
            self.publisher = self.create_publisher(
                self.message_type,
                OCCUPANCY_GRID_TOPIC,
                build_topic_qos(OCCUPANCY_GRID_TOPIC),
            )
            self.create_subscription(
                self.sensor_message_type,
                SIM_LIDAR_TOPIC,
                self._on_sensor_observation,
                build_topic_qos(SIM_LIDAR_TOPIC),
            )
            self.create_subscription(
                self.sensor_message_type,
                SIM_ULTRASONIC_TOPIC,
                self._on_sensor_observation,
                build_topic_qos(SIM_ULTRASONIC_TOPIC),
            )
            self.map_index = 0
            self.publish_count = 0
            self.last_sequence_by_sensor: dict[str, int] = {}
            self.create_timer(MAP_PUBLISH_PERIOD_SEC, self._publish_next_map)
            self.get_logger().info(
                f"Mock map node using {get_transport_mode()} transport on {OCCUPANCY_GRID_TOPIC}."
            )

        def _on_sensor_observation(self, msg) -> None:
            world = self.worlds[self.map_index]
            observation = decode_topic_message(SIM_LIDAR_TOPIC, msg)
            if observation.source_map and observation.source_map != world.mock_map.name:
                return
            previous_sequence = self.last_sequence_by_sensor.get(observation.sensor_type, -1)
            if observation.sequence_id <= previous_sequence:
                return
            step = world.apply_external_observation(observation)
            self.last_sequence_by_sensor[observation.sensor_type] = observation.sequence_id
            self.get_logger().info(
                f"Applied {observation.sensor_type} observation map={world.mock_map.name} "
                f"cells={observation.detected_cells} rev={step.occupancy_grid.revision}"
            )

        def _publish_next_map(self) -> None:
            if not self.worlds:
                return
            world = self.worlds[self.map_index]
            if self.publish_count > 0 and world.remaining_updates > 0:
                step = world.advance()
                occupancy_grid = step.occupancy_grid
                if step.applied_obstacle is not None:
                    self.get_logger().info(
                        f"Dynamic update map={world.mock_map.name} "
                        f"obstacle={step.applied_obstacle} rev={occupancy_grid.revision}"
                    )
            else:
                occupancy_grid = world.current_grid
            msg = encode_topic_message(OCCUPANCY_GRID_TOPIC, occupancy_grid, self.message_type)
            self.publisher.publish(msg)
            self.publish_count += 1
            if self.publish_count == 1 or self.publish_count % 5 == 0:
                self.get_logger().info(
                    f"Published occupancy grid map={world.mock_map.name} rev={occupancy_grid.revision} "
                    f"size={occupancy_grid.width}x{occupancy_grid.height}"
                )
            if (
                len(self.worlds) > 1
                and self.publish_count % int(MAP_ROTATION_PERIOD_SEC / MAP_PUBLISH_PERIOD_SEC) == 0
            ):
                self.map_index = (self.map_index + 1) % len(self.worlds)
                self.worlds[self.map_index].reset()
                self.last_sequence_by_sensor.clear()

    rclpy.init()
    node = MockMapNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
