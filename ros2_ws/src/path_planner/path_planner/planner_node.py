from __future__ import annotations

from autonomy_interfaces.contracts import MissionGoalMessage, OccupancyGridMessage
from autonomy_interfaces.qos import build_topic_qos
from autonomy_interfaces.topic_transport import (
    decode_topic_message,
    encode_topic_message,
    get_topic_message_type,
    get_transport_mode,
)
from mission_controller.topics import (
    MISSION_GOAL_TOPIC,
    OCCUPANCY_GRID_TOPIC,
    PLANNED_PATH_TOPIC,
    PLANNER_STATUS_TOPIC,
    REPLAN_REQUEST_TOPIC,
)

from .planning_pipeline import PlanningPipeline


def main() -> None:
    try:
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import String
    except ImportError as exc:
        raise SystemExit(
            "rclpy and std_msgs are required to run planner_node."
        ) from exc

    class PlannerNode(Node):
        def __init__(self) -> None:
            super().__init__("planner_node")
            self.pipeline = PlanningPipeline()
            self.latest_grid: OccupancyGridMessage | None = None
            self.latest_goal: MissionGoalMessage | None = None
            self.grid_message_type = get_topic_message_type(OCCUPANCY_GRID_TOPIC, String)
            self.goal_message_type = get_topic_message_type(MISSION_GOAL_TOPIC, String)
            self.path_message_type = get_topic_message_type(PLANNED_PATH_TOPIC, String)
            self.status_message_type = get_topic_message_type(PLANNER_STATUS_TOPIC, String)
            self.replan_message_type = get_topic_message_type(REPLAN_REQUEST_TOPIC, String)
            self.last_plan_signature: tuple[int, str] | None = None
            self.path_publisher = self.create_publisher(
                self.path_message_type,
                PLANNED_PATH_TOPIC,
                build_topic_qos(PLANNED_PATH_TOPIC),
            )
            self.status_publisher = self.create_publisher(
                self.status_message_type,
                PLANNER_STATUS_TOPIC,
                build_topic_qos(PLANNER_STATUS_TOPIC),
            )
            self.create_subscription(
                self.grid_message_type,
                OCCUPANCY_GRID_TOPIC,
                self._on_grid,
                build_topic_qos(OCCUPANCY_GRID_TOPIC),
            )
            self.create_subscription(
                self.goal_message_type,
                MISSION_GOAL_TOPIC,
                self._on_goal,
                build_topic_qos(MISSION_GOAL_TOPIC),
            )
            self.create_subscription(
                self.replan_message_type,
                REPLAN_REQUEST_TOPIC,
                self._on_replan_request,
                build_topic_qos(REPLAN_REQUEST_TOPIC),
            )
            self.get_logger().info(
                f"Planner node using {get_transport_mode()} transport for Person 1 topics."
            )

        def _on_grid(self, msg) -> None:
            self.latest_grid = decode_topic_message(OCCUPANCY_GRID_TOPIC, msg)
            self._plan_if_ready("map_update")

        def _on_goal(self, msg) -> None:
            self.latest_goal = decode_topic_message(MISSION_GOAL_TOPIC, msg)
            self._plan_if_ready("new_goal")

        def _on_replan_request(self, msg) -> None:
            del msg
            self._plan_if_ready("replan_request")

        def _plan_if_ready(self, trigger: str) -> None:
            if self.latest_grid is None or self.latest_goal is None:
                return
            signature = (self.latest_grid.revision, self.latest_goal.goal_id)
            if trigger == "map_update" and signature == self.last_plan_signature:
                return
            planned_path, status = self.pipeline.plan_for_goal(self.latest_grid, self.latest_goal)
            path_msg = encode_topic_message(PLANNED_PATH_TOPIC, planned_path, self.path_message_type)
            status_msg = encode_topic_message(PLANNER_STATUS_TOPIC, status, self.status_message_type)
            self.path_publisher.publish(path_msg)
            self.status_publisher.publish(status_msg)
            self.last_plan_signature = signature
            self.get_logger().info(
                f"Trigger={trigger} planner_state={status.state} goal={self.latest_goal.goal_id} "
                f"path_found={planned_path.path_found} rev={self.latest_grid.revision}"
            )

    rclpy.init()
    node = PlannerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
