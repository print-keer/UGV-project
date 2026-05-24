from __future__ import annotations

from pathlib import Path

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
            repo_root = Path(__file__).resolve().parents[4]
            maps_dir = repo_root / "simulation" / "maps"
            maps = load_all_mock_maps(maps_dir)
            self.get_logger().info(f"Loaded mock maps: {', '.join(maps)}")

    rclpy.init()
    node = MockMapNode()
    try:
        rclpy.spin_once(node, timeout_sec=0.1)
    finally:
        node.destroy_node()
        rclpy.shutdown()

