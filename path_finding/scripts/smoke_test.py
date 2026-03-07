#!/usr/bin/env python3
"""Simple non-GUI smoke test for pathfinding algorithms."""

import os
import sys
import random
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.astar_slam import AStarSLAM
from algorithms.rrt_slam import RRTSLAM
from algorithms.gat_pathfinder import GATPathfinder
from algorithms.dijkstra_algorithm import DijkstraPathfinder
from algorithms.prm_algorithm import PRMPathfinder
from algorithms.hybrid_astar import HybridAStar
from environment.environment_generator import EnvironmentGenerator


def main():
    random.seed(42)
    np.random.seed(42)

    env_gen = EnvironmentGenerator()
    environment = env_gen.generate_environment("simple_obstacles")
    start = environment["start"]
    goal = environment["goal"]
    obstacles = environment["obstacles"]

    algorithms = {
        "A* + SLAM": AStarSLAM(),
        "RRT + SLAM": RRTSLAM(),
        "GAT": GATPathfinder(),
        "Dijkstra": DijkstraPathfinder(),
        "PRM": PRMPathfinder(),
        "Hybrid A*": HybridAStar(),
    }

    failures = []

    print("Running pathfinding smoke test on simple_obstacles...\n")
    for name, algo in algorithms.items():
        try:
            path, metrics = algo.find_path(start, goal, obstacles)
            ok = path is not None and len(path) > 1 and metrics.get("success_rate", 0) > 0
            status = "PASS" if ok else "FAIL"
            print(f"{name:12} | {status} | path_len={metrics.get('path_length', 'n/a')}")
            if not ok:
                failures.append(name)
        except Exception as exc:
            print(f"{name:12} | FAIL | exception={exc}")
            failures.append(name)

    if failures:
        print("\nSmoke test FAILED for:", ", ".join(failures))
        raise SystemExit(1)

    print("\nSmoke test PASSED for all algorithms.")


if __name__ == "__main__":
    main()
