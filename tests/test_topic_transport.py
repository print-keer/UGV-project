from __future__ import annotations

import sys
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
src_root = repo_root / "ros2_ws" / "src"
for package_dir in src_root.iterdir():
    if package_dir.is_dir():
        sys.path.insert(0, str(package_dir))

from autonomy_interfaces.contracts import MissionGoalMessage
from autonomy_interfaces.topic_transport import (
    decode_topic_message,
    encode_topic_message,
    get_topic_message_type,
    get_transport_mode,
)
from mission_controller.topics import MISSION_GOAL_TOPIC


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


if __name__ == "__main__":
    unittest.main()
