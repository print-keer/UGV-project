from __future__ import annotations

from pathlib import Path
from typing import List

from autonomy_interfaces.contracts import MissionGoalMessage
from mapping.map_provider import MapProvider
from mapping.mock_maps import load_all_mock_maps
from .orchestrator import MissionOrchestrator


def run_demo() -> List[dict]:
    repo_root = Path(__file__).resolve().parents[4]
    maps_dir = repo_root / "simulation" / "maps"
    maps = load_all_mock_maps(maps_dir)

    map_provider = MapProvider()
    orchestrator = MissionOrchestrator()
    reports = []

    for mock_map in maps.values():
        occupancy_grid = map_provider.publish_map(mock_map)
        execution = orchestrator.execute(
            occupancy_grid=occupancy_grid,
            mission_goal=MissionGoalMessage(
                start_cell=mock_map.start,
                goal_cell=mock_map.goal,
                goal_id=mock_map.name,
            ),
        )
        reports.append(
            {
                "map_name": mock_map.name,
                "description": mock_map.description,
                "start": execution.mission_goal.start_cell,
                "goal": execution.mission_goal.goal_cell,
                "path_found": execution.planned_path.path_found,
                "total_cost": execution.planned_path.total_cost,
                "visited_nodes": execution.planner_status.visited_nodes,
                "path": execution.planned_path.waypoints,
                "planner_state": execution.planner_status.state,
                "navigation_state": execution.navigation_status.state,
                "navigation_message": execution.navigation_status.message,
                "replan_reason": (
                    execution.replan_request.reason if execution.replan_request else None
                ),
            }
        )
    return reports


def run_topic_demo() -> List[dict]:
    repo_root = Path(__file__).resolve().parents[4]
    maps_dir = repo_root / "simulation" / "maps"
    maps = load_all_mock_maps(maps_dir)

    map_provider = MapProvider()
    orchestrator = MissionOrchestrator()
    reports = []

    for mock_map in maps.values():
        occupancy_grid = map_provider.publish_map(mock_map)
        blocked_cell = (
            mock_map.start[0],
            mock_map.start[1] + 1,
        )
        topic_execution = orchestrator.execute_with_topics(
            occupancy_grid=occupancy_grid,
            mission_goal=MissionGoalMessage(
                start_cell=mock_map.start,
                goal_cell=mock_map.goal,
                goal_id=mock_map.name,
            ),
            blocked_cell=blocked_cell,
        )
        reports.append(
            {
                "map_name": mock_map.name,
                "replanned": topic_execution.replanned,
                "initial_revision": topic_execution.initial_execution.occupancy_grid.revision,
                "final_revision": topic_execution.final_execution.occupancy_grid.revision,
                "final_path_found": topic_execution.final_execution.planned_path.path_found,
                "published_topics": topic_execution.published_topics,
            }
        )
    return reports


def run_dynamic_demo() -> List[dict]:
    repo_root = Path(__file__).resolve().parents[4]
    maps_dir = repo_root / "simulation" / "maps"
    maps = load_all_mock_maps(maps_dir)

    orchestrator = MissionOrchestrator()
    reports = []

    for mock_map in maps.values():
        if not mock_map.dynamic_obstacles:
            continue
        dynamic_execution = orchestrator.execute_dynamic_world(mock_map)
        reports.append(
            {
                "map_name": dynamic_execution.map_name,
                "total_replans": dynamic_execution.total_replans,
                "revisions": [step.occupancy_revision for step in dynamic_execution.steps],
                "path_lengths": [len(step.path) for step in dynamic_execution.steps],
                "applied_obstacles": [
                    step.applied_obstacle for step in dynamic_execution.steps if step.applied_obstacle
                ],
            }
        )
    return reports


def main() -> int:
    reports = run_demo()
    for report in reports:
        print(report)
    topic_reports = run_topic_demo()
    for report in topic_reports:
        print(report)
    dynamic_reports = run_dynamic_demo()
    for report in dynamic_reports:
        print(report)
    return 0
