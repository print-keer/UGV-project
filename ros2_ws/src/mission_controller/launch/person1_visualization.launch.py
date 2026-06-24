from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    use_rviz = LaunchConfiguration("use_rviz")
    rviz_config = PathJoinSubstitution(
        [FindPackageShare("mission_controller"), "rviz", "person1_navigation.rviz"]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_rviz", default_value="false"),
            Node(package="mapping", executable="mock_map_node", output="screen"),
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
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                output="screen",
                arguments=["-d", rviz_config],
                condition=IfCondition(use_rviz),
            ),
        ]
    )
