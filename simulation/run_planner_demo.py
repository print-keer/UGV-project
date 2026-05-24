"""Simulation-first demo entrypoint for the navigation foundation."""

from __future__ import annotations

import sys
from pathlib import Path


def _add_ros2_src_to_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src_root = repo_root / "ros2_ws" / "src"
    for package_dir in src_root.iterdir():
        if package_dir.is_dir():
            sys.path.insert(0, str(package_dir))


def main() -> int:
    _add_ros2_src_to_path()

    from mission_controller.demo import run_demo

    reports = run_demo()
    for report in reports:
        print("=" * 60)
        print(f"Map: {report['map_name']}")
        print(f"Description: {report['description']}")
        print(f"Start: {report['start']} Goal: {report['goal']}")
        print(f"Path found: {report['path_found']}")
        print(f"Total cost: {report['total_cost']}")
        print(f"Visited nodes: {report['visited_nodes']}")
        print(f"Path: {report['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
