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
    NAV_BLOCKED,
    PLANNER_NO_PATH,
    PLANNER_SUCCESS,
    REPLAN_EMPTY_PATH,
    REPLAN_NO_PATH_RECOVERY,
    REPLAN_PATH_BLOCKED,
    MissionGoalMessage,
    PlannedPathMessage,
)
from mapping.map_provider import MapProvider
from mapping.mock_maps import MockMap
from mission_controller.orchestrator import MissionOrchestrator
from navigation.path_follower import PathFollower


class Person1InterfaceTests(unittest.TestCase):
    def test_map_provider_builds_expected_occupancy_grid_contract(self) -> None:
        mock_map = MockMap(
            name="unit_map",
            description="Map for unit testing contracts.",
            start=(0, 0),
            goal=(1, 1),
            grid=[
                [0, 2],
                [1, 0],
            ],
        )

        grid_message = MapProvider().publish_map(mock_map)

        self.assertEqual(grid_message.width, 2)
        self.assertEqual(grid_message.height, 2)
        self.assertEqual(grid_message.origin, (0, 0))
        self.assertEqual(grid_message.data, [0, 2, 1, 0])
        self.assertEqual(grid_message.revision, 0)
        self.assertEqual(grid_message.to_grid(), mock_map.grid)

    def test_mission_orchestrator_returns_pipeline_statuses(self) -> None:
        mock_map = MockMap(
            name="orchestrator_map",
            description="Reachable mission flow.",
            start=(0, 0),
            goal=(2, 2),
            grid=[
                [0, 0, 0],
                [0, 1, 0],
                [0, 0, 0],
            ],
        )

        occupancy_grid = MapProvider().publish_map(mock_map)
        execution = MissionOrchestrator().execute(
            occupancy_grid=occupancy_grid,
            mission_goal=MissionGoalMessage(
                start_cell=mock_map.start,
                goal_cell=mock_map.goal,
                goal_id=mock_map.name,
            ),
        )

        self.assertEqual(execution.planner_status.state, PLANNER_SUCCESS)
        self.assertTrue(execution.planned_path.path_found)
        self.assertEqual(execution.navigation_status.goal_id, mock_map.name)
        self.assertIsNone(execution.replan_request)

    def test_navigation_requests_replan_when_path_is_empty(self) -> None:
        follower = PathFollower()
        report = follower.consume_path(
            PlannedPathMessage(
                path_found=False,
                waypoints=[],
                total_cost=0.0,
                goal_id="blocked_goal",
            )
        )

        self.assertFalse(report.accepted)
        self.assertEqual(report.status.state, NAV_BLOCKED)
        self.assertIsNotNone(report.replan_request)
        self.assertEqual(report.replan_request.reason, REPLAN_NO_PATH_RECOVERY)

    def test_topic_orchestrator_replans_after_blocked_waypoint(self) -> None:
        mock_map = MockMap(
            name="topic_map",
            description="Map with a path that can be invalidated mid-run.",
            start=(0, 0),
            goal=(0, 3),
            grid=[
                [0, 0, 0, 0],
                [0, 1, 1, 0],
                [0, 0, 0, 0],
            ],
        )

        occupancy_grid = MapProvider().publish_map(mock_map)
        execution = MissionOrchestrator().execute_with_topics(
            occupancy_grid=occupancy_grid,
            mission_goal=MissionGoalMessage(
                start_cell=mock_map.start,
                goal_cell=mock_map.goal,
                goal_id=mock_map.name,
            ),
            blocked_cell=(0, 1),
        )

        self.assertTrue(execution.replanned)
        self.assertEqual(execution.final_execution.occupancy_grid.revision, 1)
        self.assertNotEqual(
            execution.initial_execution.planned_path.waypoints,
            execution.final_execution.planned_path.waypoints,
        )
        self.assertIn("/navigation/replan_request", execution.published_topics)

    def test_blocked_waypoint_report_uses_path_blocked_reason(self) -> None:
        follower = PathFollower()
        report = follower.detect_blocked_waypoint(
            PlannedPathMessage(
                path_found=True,
                waypoints=[(0, 0), (0, 1), (0, 2)],
                total_cost=2.0,
                goal_id="reroute_goal",
            ),
            blocked_cell=(0, 1),
        )

        self.assertFalse(report.accepted)
        self.assertEqual(report.replan_request.reason, REPLAN_PATH_BLOCKED)

    def test_dynamic_world_execution_generates_multiple_revisions(self) -> None:
        mock_map = MockMap(
            name="dynamic_world_map",
            description="Dynamic map with staged obstacles.",
            start=(0, 0),
            goal=(2, 4),
            grid=[
                [0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0],
                [0, 0, 0, 0, 0],
            ],
            dynamic_obstacles=[(0, 2), (2, 2)],
        )

        execution = MissionOrchestrator().execute_dynamic_world(mock_map)

        self.assertEqual(execution.total_replans, 2)
        self.assertEqual([step.occupancy_revision for step in execution.steps], [0, 1, 2])
        self.assertTrue(execution.steps[0].path_found)
        self.assertTrue(any(not step.path_found for step in execution.steps[1:]))

    def test_dynamic_world_reports_terminal_no_path_state(self) -> None:
        mock_map = MockMap(
            name="terminal_no_path_map",
            description="Dynamic map that becomes unsolvable.",
            start=(0, 0),
            goal=(0, 3),
            grid=[
                [0, 0, 0, 0],
                [1, 1, 1, 0],
            ],
            dynamic_obstacles=[(0, 1), (0, 2)],
        )

        execution = MissionOrchestrator().execute_dynamic_world(mock_map)

        self.assertEqual(execution.terminal_state, PLANNER_NO_PATH)
        self.assertEqual(execution.steps[-1].recovery_action, "hold_position_and_report_no_path")


if __name__ == "__main__":
    unittest.main()
