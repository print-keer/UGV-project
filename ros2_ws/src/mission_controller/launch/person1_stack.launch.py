from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            Node(package="mapping", executable="mock_map_node", output="screen"),
            Node(package="path_planner", executable="planner_node", output="screen"),
            Node(package="navigation", executable="navigation_node", output="screen"),
            Node(
                package="mission_controller",
                executable="mission_controller_node",
                output="screen",
            ),
        ]
    )
