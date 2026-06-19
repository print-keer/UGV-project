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
)
from mission_controller.visualization_snapshot import build_visualization_snapshot


class VisualizationSnapshotTests(unittest.TestCase):
    def test_snapshot_summarizes_map_path_and_status(self) -> None:
        snapshot = build_visualization_snapshot(
            OccupancyGridMessage(
                width=3,
                height=2,
                resolution=1.0,
                origin=(0, 0),
                data=[0, 1, 2, 0, 0, 1],
            ),
            planned_path=PlannedPathMessage(
                path_found=True,
                waypoints=[(0, 0), (0, 1), (1, 1)],
                total_cost=2.0,
                goal_id="viz_goal",
            ),
            mission_goal=MissionGoalMessage(
                start_cell=(0, 0),
                goal_cell=(1, 1),
                goal_id="viz_goal",
            ),
            navigation_status=NavigationStatusMessage(
                state="reached_goal",
                message="Done.",
                current_cell=(1, 1),
                current_waypoint_index=2,
                goal_id="viz_goal",
                path_length=3,
            ),
        )

        self.assertEqual(snapshot.map_width, 3)
        self.assertEqual(snapshot.map_height, 2)
        self.assertEqual(snapshot.occupied_cells, 2)
        self.assertEqual(snapshot.unknown_cells, 1)
        self.assertEqual(snapshot.path_length, 3)
        self.assertEqual(snapshot.goal_cell, (1, 1))
        self.assertEqual(snapshot.current_cell, (1, 1))
        self.assertTrue(snapshot.reached_goal)


if __name__ == "__main__":
    unittest.main()
