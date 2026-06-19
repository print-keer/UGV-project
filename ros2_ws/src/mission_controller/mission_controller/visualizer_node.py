from __future__ import annotations

from autonomy_interfaces.contracts import (
    MissionGoalMessage,
    NavigationStatusMessage,
    OccupancyGridMessage,
    PlannedPathMessage,
)
from autonomy_interfaces.qos import build_topic_qos
from autonomy_interfaces.topic_transport import (
    decode_topic_message,
    get_topic_message_type,
    get_transport_mode,
)
from .topics import (
    MISSION_GOAL_TOPIC,
    NAVIGATION_STATUS_TOPIC,
    OCCUPANCY_GRID_TOPIC,
    PLANNED_PATH_TOPIC,
    VIZ_GOAL_TOPIC,
    VIZ_MARKERS_TOPIC,
    VIZ_OCCUPANCY_GRID_TOPIC,
    VIZ_PLANNED_PATH_TOPIC,
)
from .visualization_snapshot import build_visualization_snapshot


def main() -> None:
    try:
        import rclpy
        from geometry_msgs.msg import Point, PoseStamped
        from nav_msgs.msg import OccupancyGrid, Path
        from rclpy.node import Node
        from std_msgs.msg import Header, String
        from visualization_msgs.msg import Marker, MarkerArray
    except ImportError as exc:
        raise SystemExit(
            "rclpy, nav_msgs, geometry_msgs, and visualization_msgs are required to run visualizer_node."
        ) from exc

    class VisualizerNode(Node):
        def __init__(self) -> None:
            super().__init__("visualizer_node")
            self.goal_message_type = get_topic_message_type(MISSION_GOAL_TOPIC, String)
            self.grid_message_type = get_topic_message_type(OCCUPANCY_GRID_TOPIC, String)
            self.path_message_type = get_topic_message_type(PLANNED_PATH_TOPIC, String)
            self.navigation_message_type = get_topic_message_type(NAVIGATION_STATUS_TOPIC, String)

            self.latest_goal: MissionGoalMessage | None = None
            self.latest_grid: OccupancyGridMessage | None = None
            self.latest_path: PlannedPathMessage | None = None
            self.latest_navigation: NavigationStatusMessage | None = None

            self.grid_publisher = self.create_publisher(
                OccupancyGrid,
                VIZ_OCCUPANCY_GRID_TOPIC,
                build_topic_qos(VIZ_OCCUPANCY_GRID_TOPIC),
            )
            self.path_publisher = self.create_publisher(
                Path,
                VIZ_PLANNED_PATH_TOPIC,
                build_topic_qos(VIZ_PLANNED_PATH_TOPIC),
            )
            self.goal_publisher = self.create_publisher(
                PoseStamped,
                VIZ_GOAL_TOPIC,
                build_topic_qos(VIZ_GOAL_TOPIC),
            )
            self.marker_publisher = self.create_publisher(
                MarkerArray,
                VIZ_MARKERS_TOPIC,
                build_topic_qos(VIZ_MARKERS_TOPIC),
            )

            self.create_subscription(
                self.goal_message_type,
                MISSION_GOAL_TOPIC,
                self._on_goal,
                build_topic_qos(MISSION_GOAL_TOPIC),
            )
            self.create_subscription(
                self.grid_message_type,
                OCCUPANCY_GRID_TOPIC,
                self._on_grid,
                build_topic_qos(OCCUPANCY_GRID_TOPIC),
            )
            self.create_subscription(
                self.path_message_type,
                PLANNED_PATH_TOPIC,
                self._on_path,
                build_topic_qos(PLANNED_PATH_TOPIC),
            )
            self.create_subscription(
                self.navigation_message_type,
                NAVIGATION_STATUS_TOPIC,
                self._on_navigation,
                build_topic_qos(NAVIGATION_STATUS_TOPIC),
            )
            self.get_logger().info(
                f"Visualizer node using {get_transport_mode()} transport for Person 1 topics."
            )

        def _on_goal(self, msg) -> None:
            self.latest_goal = decode_topic_message(MISSION_GOAL_TOPIC, msg)
            self._publish_visual_state()

        def _on_grid(self, msg) -> None:
            self.latest_grid = decode_topic_message(OCCUPANCY_GRID_TOPIC, msg)
            self._publish_visual_state()

        def _on_path(self, msg) -> None:
            self.latest_path = decode_topic_message(PLANNED_PATH_TOPIC, msg)
            self._publish_visual_state()

        def _on_navigation(self, msg) -> None:
            self.latest_navigation = decode_topic_message(NAVIGATION_STATUS_TOPIC, msg)
            self._publish_visual_state()

        def _publish_visual_state(self) -> None:
            if self.latest_grid is None:
                return

            snapshot = build_visualization_snapshot(
                self.latest_grid,
                planned_path=self.latest_path,
                mission_goal=self.latest_goal,
                navigation_status=self.latest_navigation,
            )

            self.grid_publisher.publish(self._to_nav_occupancy_grid(self.latest_grid))
            if self.latest_path is not None:
                self.path_publisher.publish(self._to_nav_path(self.latest_path))
            if self.latest_goal is not None:
                self.goal_publisher.publish(self._to_goal_pose(self.latest_goal))
            self.marker_publisher.publish(self._to_marker_array(snapshot))

        def _header(self) -> Header:
            return Header(frame_id="map", stamp=self.get_clock().now().to_msg())

        def _to_nav_occupancy_grid(self, occupancy_grid: OccupancyGridMessage) -> OccupancyGrid:
            grid = OccupancyGrid()
            grid.header = self._header()
            grid.info.resolution = float(occupancy_grid.resolution)
            grid.info.width = occupancy_grid.width
            grid.info.height = occupancy_grid.height
            grid.info.origin.position.x = float(occupancy_grid.origin[1])
            grid.info.origin.position.y = float(occupancy_grid.origin[0])
            grid.info.origin.orientation.w = 1.0
            grid.data = [100 if value == 1 else -1 if value == 2 else 0 for value in occupancy_grid.data]
            return grid

        def _to_nav_path(self, planned_path: PlannedPathMessage) -> Path:
            path = Path()
            path.header = self._header()
            path.poses = []
            for row, col in planned_path.waypoints:
                pose = PoseStamped()
                pose.header = path.header
                pose.pose.position.x = float(col)
                pose.pose.position.y = float(row)
                pose.pose.orientation.w = 1.0
                path.poses.append(pose)
            return path

        def _to_goal_pose(self, mission_goal: MissionGoalMessage) -> PoseStamped:
            pose = PoseStamped()
            pose.header = self._header()
            pose.pose.position.x = float(mission_goal.goal_cell[1])
            pose.pose.position.y = float(mission_goal.goal_cell[0])
            pose.pose.orientation.w = 1.0
            return pose

        def _to_marker_array(self, snapshot) -> MarkerArray:
            marker_array = MarkerArray()
            markers: list[Marker] = []
            if snapshot.goal_cell is not None:
                goal_marker = Marker()
                goal_marker.header = self._header()
                goal_marker.ns = "goal"
                goal_marker.id = 1
                goal_marker.type = Marker.SPHERE
                goal_marker.action = Marker.ADD
                goal_marker.pose.position.x = float(snapshot.goal_cell[1])
                goal_marker.pose.position.y = float(snapshot.goal_cell[0])
                goal_marker.pose.orientation.w = 1.0
                goal_marker.scale.x = goal_marker.scale.y = goal_marker.scale.z = 0.35
                goal_marker.color.a = 1.0
                goal_marker.color.r = 0.1
                goal_marker.color.g = 0.9
                goal_marker.color.b = 0.1
                markers.append(goal_marker)

            if snapshot.current_cell is not None:
                current_marker = Marker()
                current_marker.header = self._header()
                current_marker.ns = "current_cell"
                current_marker.id = 2
                current_marker.type = Marker.CUBE
                current_marker.action = Marker.ADD
                current_marker.pose.position.x = float(snapshot.current_cell[1])
                current_marker.pose.position.y = float(snapshot.current_cell[0])
                current_marker.pose.orientation.w = 1.0
                current_marker.scale.x = current_marker.scale.y = current_marker.scale.z = 0.28
                current_marker.color.a = 1.0
                current_marker.color.r = 0.1
                current_marker.color.g = 0.4
                current_marker.color.b = 1.0
                markers.append(current_marker)

            text_marker = Marker()
            text_marker.header = self._header()
            text_marker.ns = "summary"
            text_marker.id = 3
            text_marker.type = Marker.TEXT_VIEW_FACING
            text_marker.action = Marker.ADD
            text_marker.pose.position.x = 0.0
            text_marker.pose.position.y = -1.0
            text_marker.pose.orientation.w = 1.0
            text_marker.scale.z = 0.35
            text_marker.color.a = 1.0
            text_marker.color.r = 1.0
            text_marker.color.g = 1.0
            text_marker.color.b = 1.0
            text_marker.text = (
                f"map={snapshot.map_width}x{snapshot.map_height} "
                f"occupied={snapshot.occupied_cells} unknown={snapshot.unknown_cells} "
                f"path={snapshot.path_length} reached_goal={snapshot.reached_goal}"
            )
            markers.append(text_marker)

            marker_array.markers = markers
            return marker_array

    rclpy.init()
    node = VisualizerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()

