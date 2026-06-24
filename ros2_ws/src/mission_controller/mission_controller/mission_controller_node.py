from __future__ import annotations

from pathlib import Path

from autonomy_interfaces.contracts import (
    MissionGoalMessage,
    MissionStateMessage,
    MotorStatusMessage,
    NavigationStatusMessage,
    PlannerStatusMessage,
    ReplanRequestMessage,
)
from autonomy_interfaces.qos import build_topic_qos
from autonomy_interfaces.topic_transport import (
    decode_topic_message,
    encode_topic_message,
    get_topic_message_type,
    get_transport_mode,
)
from .topics import (
    MISSION_GOAL_PERIOD_SEC,
    MISSION_GOAL_TOPIC,
    MISSION_STATE_TOPIC,
    MOTOR_STATUS_TOPIC,
    NAVIGATION_STATUS_TOPIC,
    PLANNER_STATUS_TOPIC,
    REPLAN_REQUEST_TOPIC,
)
from .mission_policy import (
    MISSION_ACTION_HALT_MISSION,
    MISSION_ACTION_REPUBLISH_GOAL,
    MISSION_ACTION_REQUEST_REPLAN,
    MissionPolicy,
)
from .mission_state_machine import MissionStateMachine


def main() -> None:
    try:
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import String
    except ImportError as exc:
        raise SystemExit(
            "rclpy and std_msgs are required to run mission_controller_node."
        ) from exc

    class MissionControllerNode(Node):
        def __init__(self) -> None:
            super().__init__("mission_controller_node")
            self.goal_message_type = get_topic_message_type(MISSION_GOAL_TOPIC, String)
            self.planner_status_type = get_topic_message_type(PLANNER_STATUS_TOPIC, String)
            self.navigation_status_type = get_topic_message_type(NAVIGATION_STATUS_TOPIC, String)
            self.motor_status_type = get_topic_message_type(MOTOR_STATUS_TOPIC, String)
            self.mission_state_type = get_topic_message_type(MISSION_STATE_TOPIC, String)
            self.replan_request_type = get_topic_message_type(REPLAN_REQUEST_TOPIC, String)
            self.state_machine = MissionStateMachine()
            self.policy = MissionPolicy()
            self.goal = MissionGoalMessage(
                start_cell=(0, 0),
                goal_cell=(5, 5),
                goal_id="mission_demo_goal",
            )
            self.goal_publish_count = 0
            self.mission_active = True
            self.goal_publisher = self.create_publisher(
                self.goal_message_type,
                MISSION_GOAL_TOPIC,
                build_topic_qos(MISSION_GOAL_TOPIC),
            )
            self.mission_state_publisher = self.create_publisher(
                self.mission_state_type,
                MISSION_STATE_TOPIC,
                build_topic_qos(MISSION_STATE_TOPIC),
            )
            self.replan_request_publisher = self.create_publisher(
                self.replan_request_type,
                REPLAN_REQUEST_TOPIC,
                build_topic_qos(REPLAN_REQUEST_TOPIC),
            )
            self.create_subscription(
                self.planner_status_type,
                PLANNER_STATUS_TOPIC,
                self._on_planner_status,
                build_topic_qos(PLANNER_STATUS_TOPIC),
            )
            self.create_subscription(
                self.navigation_status_type,
                NAVIGATION_STATUS_TOPIC,
                self._on_navigation_status,
                build_topic_qos(NAVIGATION_STATUS_TOPIC),
            )
            self.create_subscription(
                self.motor_status_type,
                MOTOR_STATUS_TOPIC,
                self._on_motor_status,
                build_topic_qos(MOTOR_STATUS_TOPIC),
            )
            self.create_timer(MISSION_GOAL_PERIOD_SEC, self._publish_goal)
            self.get_logger().info(
                f"Mission controller using {get_transport_mode()} transport for Person 1 topics."
            )
            self._publish_goal()

        def _publish_goal(self, *, policy_triggered: bool = False) -> None:
            if not self.mission_active and not policy_triggered:
                return
            repo_root = Path(__file__).resolve().parents[4]
            msg = encode_topic_message(MISSION_GOAL_TOPIC, self.goal, self.goal_message_type)
            self.goal_publisher.publish(msg)
            state = self.state_machine.on_goal(self.goal)
            self.policy.on_goal(self.goal)
            self._publish_mission_state(state)
            self.goal_publish_count += 1
            if self.goal_publish_count == 1 or self.goal_publish_count % 5 == 0:
                self.get_logger().info(
                    f"Published mission goal from {repo_root.name}: {self.goal}"
                )

        def _on_planner_status(self, msg) -> None:
            status = decode_topic_message(PLANNER_STATUS_TOPIC, msg)
            self._publish_mission_state(self.state_machine.on_planner_status(status))
            self.get_logger().info(
                f"Planner status goal_id={status.goal_id} state={status.state} visited={status.visited_nodes}"
            )

        def _on_navigation_status(self, msg) -> None:
            status = decode_topic_message(NAVIGATION_STATUS_TOPIC, msg)
            self._publish_mission_state(self.state_machine.on_navigation_status(status))
            self.get_logger().info(
                f"Navigation status goal_id={status.goal_id} state={status.state} current={status.current_cell}"
            )

        def _on_motor_status(self, msg) -> None:
            status = decode_topic_message(MOTOR_STATUS_TOPIC, msg)
            self._publish_mission_state(self.state_machine.on_motor_status(status))
            self.get_logger().info(
                f"Motor status goal_id={status.goal_id} mode={status.mode} state={status.state} "
                f"left={status.left_wheel_speed:.2f} right={status.right_wheel_speed:.2f} "
                f"estop={status.emergency_stop}"
            )

        def _publish_mission_state(self, state: MissionStateMessage) -> None:
            msg = encode_topic_message(MISSION_STATE_TOPIC, state, self.mission_state_type)
            self.mission_state_publisher.publish(msg)
            self.get_logger().info(
                f"Mission state goal_id={state.goal_id} state={state.state} detail={state.detail}"
            )
            self._apply_policy_actions(state)

        def _apply_policy_actions(self, state: MissionStateMessage) -> None:
            for action in self.policy.on_state(state):
                if action.action_type == MISSION_ACTION_REPUBLISH_GOAL:
                    self.get_logger().info(action.detail)
                    self._publish_goal(policy_triggered=True)
                elif action.action_type == MISSION_ACTION_REQUEST_REPLAN:
                    request = ReplanRequestMessage(
                        reason=action.reason,
                        goal_id=self.goal.goal_id,
                    )
                    msg = encode_topic_message(
                        REPLAN_REQUEST_TOPIC,
                        request,
                        self.replan_request_type,
                    )
                    self.replan_request_publisher.publish(msg)
                    self.get_logger().info(action.detail)
                elif action.action_type == MISSION_ACTION_HALT_MISSION:
                    self.mission_active = False
                    self.get_logger().info(action.detail)

    rclpy.init()
    node = MissionControllerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
