from __future__ import annotations

from pathlib import Path
from typing import List

from mapping.mock_maps import load_all_mock_maps
from navigation.path_follower import PathFollower
from path_planner.astar import AStarPlanner


def run_demo() -> List[dict]:
    repo_root = Path(__file__).resolve().parents[4]
    maps_dir = repo_root / "simulation" / "maps"
    maps = load_all_mock_maps(maps_dir)

    planner = AStarPlanner()
    follower = PathFollower()
    reports = []

    for mock_map in maps.values():
        result = planner.plan(mock_map.grid, mock_map.start, mock_map.goal)
        nav_report = follower.consume_path(result.path)
        reports.append(
            {
                "map_name": mock_map.name,
                "description": mock_map.description,
                "start": mock_map.start,
                "goal": mock_map.goal,
                "path_found": result.path_found,
                "total_cost": result.total_cost,
                "visited_nodes": result.visited_nodes,
                "path": result.path,
                "navigation_message": nav_report.message,
            }
        )
    return reports


def main() -> int:
    reports = run_demo()
    for report in reports:
        print(report)
    return 0

