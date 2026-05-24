from __future__ import annotations

import json
from pathlib import Path

from .astar import AStarPlanner


def _load_demo_map() -> dict:
    repo_root = Path(__file__).resolve().parents[4]
    map_path = repo_root / "simulation" / "maps" / "map_corridor.json"
    return json.loads(map_path.read_text(encoding="utf-8"))


def main() -> None:
    try:
        import rclpy
        from rclpy.node import Node
    except ImportError as exc:
        raise SystemExit(
            "rclpy is required to run planner_node. Use the pure Python demo or install ROS2 Humble."
        ) from exc

    class PlannerNode(Node):
        def __init__(self) -> None:
            super().__init__("planner_node")
            planner = AStarPlanner()
            demo_map = _load_demo_map()
            result = planner.plan(
                demo_map["grid"],
                tuple(demo_map["start"]),
                tuple(demo_map["goal"]),
            )
            self.get_logger().info(
                f"Planned path_found={result.path_found} total_cost={result.total_cost} path={result.path}"
            )

    rclpy.init()
    node = PlannerNode()
    try:
        rclpy.spin_once(node, timeout_sec=0.1)
    finally:
        node.destroy_node()
        rclpy.shutdown()

