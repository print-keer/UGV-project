from __future__ import annotations

import sys
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
src_root = repo_root / "ros2_ws" / "src"
for package_dir in src_root.iterdir():
    if package_dir.is_dir():
        sys.path.insert(0, str(package_dir))

from path_planner.astar import AStarPlanner
from path_planner.types import PlannerConfig


class AStarPlannerTests(unittest.TestCase):
    def test_astar_finds_shortest_path_on_clear_grid(self) -> None:
        planner = AStarPlanner()
        grid = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
        result = planner.plan(grid, (0, 0), (2, 2))

        self.assertTrue(result.path_found)
        self.assertEqual(result.path[0], (0, 0))
        self.assertEqual(result.path[-1], (2, 2))
        self.assertEqual(len(result.path), 5)

    def test_astar_reports_no_path_when_goal_is_blocked(self) -> None:
        planner = AStarPlanner()
        grid = [
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ]
        result = planner.plan(grid, (0, 0), (2, 2))

        self.assertFalse(result.path_found)
        self.assertEqual(result.path, [])
        self.assertIn("not traversable", result.message)

    def test_astar_avoids_obstacle_cells(self) -> None:
        planner = AStarPlanner()
        grid = [
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        result = planner.plan(grid, (0, 0), (3, 3))

        self.assertTrue(result.path_found)
        self.assertTrue(all(grid[row][col] != 1 for row, col in result.path))

    def test_unknown_cells_are_allowed_by_default_with_added_cost(self) -> None:
        planner = AStarPlanner(PlannerConfig(unknown_cell_penalty=7.0))
        grid = [
            [0, 2, 0],
            [1, 1, 0],
            [0, 0, 0],
        ]
        result = planner.plan(grid, (0, 0), (0, 2))

        self.assertTrue(result.path_found)
        self.assertIn((0, 1), result.path)
        self.assertGreater(result.total_cost, 2.0)

    def test_unknown_cells_can_be_marked_non_traversable(self) -> None:
        planner = AStarPlanner(PlannerConfig(allow_unknown_cells=False))
        grid = [
            [0, 2, 0],
            [1, 1, 0],
            [0, 0, 0],
        ]
        result = planner.plan(grid, (0, 0), (0, 2))

        self.assertFalse(result.path_found)
        self.assertIn("No path found", result.message)


if __name__ == "__main__":
    unittest.main()
