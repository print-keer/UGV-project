from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    lidar_params = PathJoinSubstitution(
        [FindPackageShare("mission_controller"), "config", "lidar_adapter_defaults.yaml"]
    )
    ultrasonic_params = PathJoinSubstitution(
        [FindPackageShare("mission_controller"), "config", "ultrasonic_adapter_defaults.yaml"]
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument("scan_topic", default_value="/scan"),
            DeclareLaunchArgument("ultrasonic_topic", default_value="/ultrasonic/range"),
            Node(package="mapping", executable="mock_map_node", output="screen"),
            Node(
                package="mapping",
                executable="lidar_adapter_node",
                output="screen",
                parameters=[
                    lidar_params,
                    {"input_topic": LaunchConfiguration("scan_topic")},
                ],
            ),
            Node(
                package="mapping",
                executable="ultrasonic_adapter_node",
                output="screen",
                parameters=[
                    ultrasonic_params,
                    {"input_topic": LaunchConfiguration("ultrasonic_topic")},
                ],
            ),
            Node(package="path_planner", executable="planner_node", output="screen"),
            Node(package="navigation", executable="navigation_node", output="screen"),
            Node(package="navigation", executable="motion_adapter_node", output="screen"),
            Node(package="motor_controller", executable="motor_controller_node", output="screen"),
            Node(
                package="mission_controller",
                executable="mission_controller_node",
                output="screen",
            ),
            Node(
                package="mission_controller",
                executable="visualizer_node",
                output="screen",
            ),
            Node(
                package="mission_controller",
                executable="monitor_node",
                output="screen",
            ),
        ]
    )
