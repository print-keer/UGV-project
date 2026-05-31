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
    NavigationStatusMessage,
    OccupancyGridMessage,
    PlannedPathMessage,
    PlannerStatusMessage,
    ReplanRequestMessage,
)
from autonomy_interfaces.serialization import deserialize_message, serialize_message


class ContractSerializationTests(unittest.TestCase):
    def test_occupancy_grid_round_trip(self) -> None:
        original = OccupancyGridMessage(
            width=2,
            height=2,
            resolution=1.0,
            origin=(1, 2),
            data=[0, 1, 2, 0],
            source_map="unit",
            revision=3,
        )

        restored = deserialize_message(serialize_message(original), OccupancyGridMessage)

        self.assertEqual(restored, original)

    def test_goal_and_path_round_trip(self) -> None:
        goal = MissionGoalMessage(start_cell=(0, 0), goal_cell=(3, 4), goal_id="goal_a")
        path = PlannedPathMessage(path_found=True, waypoints=[(0, 0), (0, 1)], total_cost=1.0, goal_id="goal_a")

        self.assertEqual(deserialize_message(serialize_message(goal), MissionGoalMessage), goal)
        self.assertEqual(deserialize_message(serialize_message(path), PlannedPathMessage), path)

    def test_extended_status_round_trip(self) -> None:
        planner_status = PlannerStatusMessage(
            state="success",
            message="Path found.",
            goal_id="goal_a",
            visited_nodes=11,
            start_cell=(0, 0),
            goal_cell=(2, 2),
            occupancy_revision=3,
        )
        navigation_status = NavigationStatusMessage(
            state="following_path",
            message="Accepted path.",
            current_cell=(2, 2),
            current_waypoint_index=4,
            goal_id="goal_a",
            path_length=5,
        )
        replan_request = ReplanRequestMessage(
            reason="path_blocked",
            current_cell=(1, 1),
            goal_id="goal_a",
            occupancy_revision=3,
        )

        self.assertEqual(
            deserialize_message(serialize_message(planner_status), PlannerStatusMessage),
            planner_status,
        )
        self.assertEqual(
            deserialize_message(serialize_message(navigation_status), NavigationStatusMessage),
            navigation_status,
        )
        self.assertEqual(
            deserialize_message(serialize_message(replan_request), ReplanRequestMessage),
            replan_request,
        )


if __name__ == "__main__":
    unittest.main()
