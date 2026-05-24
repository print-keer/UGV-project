from __future__ import annotations


def main() -> None:
    try:
        import rclpy
        from rclpy.node import Node
    except ImportError as exc:
        raise SystemExit(
            "rclpy is required to run navigation_node. Use the pure Python demo or install ROS2 Humble."
        ) from exc

    class NavigationNode(Node):
        def __init__(self) -> None:
            super().__init__("navigation_node")
            self.get_logger().info("Navigation node scaffold is ready for path subscriptions.")

    rclpy.init()
    node = NavigationNode()
    try:
        rclpy.spin_once(node, timeout_sec=0.1)
    finally:
        node.destroy_node()
        rclpy.shutdown()

