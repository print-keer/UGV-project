from __future__ import annotations

import sys
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
src_root = repo_root / "ros2_ws" / "src"
for package_dir in src_root.iterdir():
    if package_dir.is_dir():
        sys.path.insert(0, str(package_dir))

from autonomy_interfaces.contracts import (
    MissionGoalMessage,
    MissionStateMessage,
    MotionCommandMessage,
    MotorStatusMessage,
    SensorObservationMessage,
)
from autonomy_interfaces.topic_transport import (
    decode_topic_message,
    encode_topic_message,
    get_topic_message_type,
    get_transport_mode,
)
from mission_controller.topics import (
    MISSION_GOAL_TOPIC,
    MISSION_STATE_TOPIC,
    MOTOR_STATUS_TOPIC,
    MOTION_COMMAND_TOPIC,
    SIM_LIDAR_TOPIC,
)


class _FakeString:
    def __init__(self) -> None:
        self.data = ""


class TopicTransportTests(unittest.TestCase):
    def test_fallback_transport_uses_string_messages_when_ros_types_unavailable(self) -> None:
        message_type = get_topic_message_type(MISSION_GOAL_TOPIC, _FakeString)
        self.assertIs(message_type, _FakeString)
        self.assertEqual(get_transport_mode(), "string")

    def test_goal_round_trip_through_topic_transport(self) -> None:
        original = MissionGoalMessage(start_cell=(0, 0), goal_cell=(2, 3), goal_id="goal_transport")

        encoded = encode_topic_message(MISSION_GOAL_TOPIC, original, _FakeString)
        restored = decode_topic_message(MISSION_GOAL_TOPIC, encoded)

        self.assertEqual(restored, original)

    def test_sensor_round_trip_through_topic_transport(self) -> None:
        original = SensorObservationMessage(
            sensor_type="lidar",
            detected_cells=[(0, 1), (0, 2)],
            source_map="corridor",
            sequence_id=2,
        )

        encoded = encode_topic_message(SIM_LIDAR_TOPIC, original, _FakeString)
        restored = decode_topic_message(SIM_LIDAR_TOPIC, encoded)

        self.assertEqual(restored, original)

    def test_motion_command_round_trip_through_topic_transport(self) -> None:
        original = MotionCommandMessage(
            command_type="stop_at_goal",
            target_cell=(4, 4),
            linear_velocity=0.0,
            angular_velocity=0.0,
            stop=True,
            goal_id="goal_transport",
            sequence_id=3,
        )

        encoded = encode_topic_message(MOTION_COMMAND_TOPIC, original, _FakeString)
        restored = decode_topic_message(MOTION_COMMAND_TOPIC, encoded)

        self.assertEqual(restored, original)

    def test_motor_status_round_trip_through_topic_transport(self) -> None:
        original = MotorStatusMessage(
            state="applied",
            mode="hold",
            applied=True,
            brake=True,
            emergency_stop=False,
            target_cell=None,
            applied_forward_speed=0.0,
            applied_turn_rate=0.0,
            left_wheel_speed=0.0,
            right_wheel_speed=0.0,
            goal_id="goal_transport",
            sequence_id=5,
            detail="hold",
        )

        encoded = encode_topic_message(MOTOR_STATUS_TOPIC, original, _FakeString)
        restored = decode_topic_message(MOTOR_STATUS_TOPIC, encoded)

        self.assertEqual(restored, original)

    def test_mission_state_round_trip_through_topic_transport(self) -> None:
        original = MissionStateMessage(
            state="holding",
            detail="Motor layer is holding position.",
            goal_id="goal_transport",
            planner_state="success",
            navigation_state="blocked",
            motor_mode="hold",
            motor_state="applied",
            emergency_stop=False,
        )

        encoded = encode_topic_message(MISSION_STATE_TOPIC, original, _FakeString)
        restored = decode_topic_message(MISSION_STATE_TOPIC, encoded)

        self.assertEqual(restored, original)


if __name__ == "__main__":
    unittest.main()
