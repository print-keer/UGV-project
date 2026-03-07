"""
Unified Backend Runner for Pathfinding Algorithms
Integrates A*, Dijkstra, RRT, and DWA algorithms for the UGV pathfinding project.
Compatible with GUI system and standalone analysis.
"""

import numpy as np
import matplotlib.pyplot as plt
import time
import math
import os
from datetime import datetime


# =====================================================================
# Basic Abstract Class
# =====================================================================
class SimplePathfinder:
    """Base class for all pathfinding algorithms."""
    def __init__(self, name):
        self.name = name

    def plan_path(self, start, goal, obstacles, bounds):
        raise NotImplementedError


# =====================================================================
# A* Algorithm
# =====================================================================
class AStarPlanner(SimplePathfinder):
    def __init__(self):
        super().__init__("A*")

    def plan_path(self, start, goal, obstacles, bounds):
        grid_size = 1.0
        start_grid = (int(start[0] / grid_size), int(start[1] / grid_size))
        goal_grid = (int(goal[0] / grid_size), int(goal[1] / grid_size))

        obstacle_set = set()
        for obs in obstacles:
            for x in range(int(obs[0] / grid_size), int(obs[2] / grid_size) + 1):
                for y in range(int(obs[1] / grid_size), int(obs[3] / grid_size) + 1):
                    obstacle_set.add((x, y))

        open_set = [start_grid]
        came_from = {}
        g_score = {start_grid: 0}

        while open_set:
            current = min(open_set, key=lambda x: g_score.get(x, float("inf"))
                          + np.linalg.norm(np.array(x) - np.array(goal_grid)))

            if current == goal_grid:
                path = []
                while current in came_from:
                    path.append([current[0] * grid_size, current[1] * grid_size])
                    current = came_from[current]
                path.append(start)
                return path[::-1]

            open_set.remove(current)

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1),
                           (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if neighbor in obstacle_set:
                    continue

                tentative_g = g_score[current] + np.sqrt(dx * dx + dy * dy)
                if tentative_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    if neighbor not in open_set:
                        open_set.append(neighbor)
        return []


# =====================================================================
# Dijkstra Algorithm
# =====================================================================
class DijkstraPlanner(SimplePathfinder):
    def __init__(self):
        super().__init__("Dijkstra")

    def plan_path(self, start, goal, obstacles, bounds):
        grid_size = 1.0
        start_grid = (int(start[0] / grid_size), int(start[1] / grid_size))
        goal_grid = (int(goal[0] / grid_size), int(goal[1] / grid_size))

        obstacle_set = set()
        for obs in obstacles:
            for x in range(int(obs[0] / grid_size), int(obs[2] / grid_size) + 1):
                for y in range(int(obs[1] / grid_size), int(obs[3] / grid_size) + 1):
                    obstacle_set.add((x, y))

        unvisited = {start_grid}
        distances = {start_grid: 0}
        came_from = {}

        while unvisited:
            current = min(unvisited, key=lambda x: distances.get(x, float("inf")))
            if current == goal_grid:
                path = []
                while current in came_from:
                    path.append([current[0] * grid_size, current[1] * grid_size])
                    current = came_from[current]
                path.append(start)
                return path[::-1]

            unvisited.remove(current)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if neighbor in obstacle_set:
                    continue

                new_distance = distances[current] + 1
                if new_distance < distances.get(neighbor, float("inf")):
                    distances[neighbor] = new_distance
                    came_from[neighbor] = current
                    unvisited.add(neighbor)
        return []


# =====================================================================
# Rapidly-exploring Random Tree (RRT)
# =====================================================================
class RRTPlanner(SimplePathfinder):
    def __init__(self):
        super().__init__("RRT")

    def plan_path(self, start, goal, obstacles, bounds):
        nodes = [start]
        parent = {0: None}

        for _ in range(500):
            rand_point = goal if np.random.random() < 0.1 else [
                np.random.uniform(bounds[0], bounds[1]),
                np.random.uniform(bounds[2], bounds[3])
            ]
            distances = [np.linalg.norm(np.array(node) - np.array(rand_point)) for node in nodes]
            nearest_idx = np.argmin(distances)
            nearest = nodes[nearest_idx]
            direction = np.array(rand_point) - np.array(nearest)
            dist = np.linalg.norm(direction)
            if dist > 2.0:
                direction = direction / dist * 2.0

            new_point = (np.array(nearest) + direction).tolist()

            collision = False
            for obs in obstacles:
                if (obs[0] <= new_point[0] <= obs[2] and obs[1] <= new_point[1] <= obs[3]):
                    collision = True
                    break

            if not collision:
                nodes.append(new_point)
                parent[len(nodes) - 1] = nearest_idx

                if np.linalg.norm(np.array(new_point) - np.array(goal)) < 1.0:
                    path = []
                    current_idx = len(nodes) - 1
                    while current_idx is not None:
                        path.append(nodes[current_idx])
                        current_idx = parent[current_idx]
                    return path[::-1]
        return []


# =====================================================================
# Dynamic Window Approach (simplified for GUI)
# =====================================================================
class DWAPlanner(SimplePathfinder):
    def __init__(self):
        super().__init__("DWA")

    def plan_path(self, start, goal, obstacles, bounds):
        path = [start]
        current = np.array(start)
        goal_pos = np.array(goal)

        for _ in range(300):
            if np.linalg.norm(current - goal_pos) < 0.8:
                break

            direction = goal_pos - current
            direction = direction / (np.linalg.norm(direction) + 1e-6)
            next_pos = current + direction * 0.5

            for obs in obstacles:
                if (obs[0] <= next_pos[0] <= obs[2] and obs[1] <= next_pos[1] <= obs[3]):
                    direction = np.array([-direction[1], direction[0]])
                    next_pos = current + direction * 0.5
                    break

            current = next_pos
            path.append(current.tolist())
        return path


# =====================================================================
# Unified Backend Runner
# =====================================================================
class PathfindingBackend:
    def __init__(self):
        self.algorithms = {
            "A*": AStarPlanner(),
            "Dijkstra": DijkstraPlanner(),
            "RRT": RRTPlanner(),
            "DWA": DWAPlanner()
        }

    def execute_algorithm(self, selected_algorithm, start, goal, obstacles, slam_data=None, visualize=False):
        if selected_algorithm not in self.algorithms:
            raise ValueError(f"Algorithm {selected_algorithm} not found.")
        algo = self.algorithms[selected_algorithm]

        start_time = time.time()
        path = algo.plan_path(start, goal, obstacles, [0, 20, 0, 20])
        exec_time = time.time() - start_time

        if len(path) < 2:
            metrics = {'path_length': float('inf'), 'execution_time': exec_time, 'success': False}
            return None, metrics

        path_np = np.array(path)
        path_length = np.sum(np.linalg.norm(np.diff(path_np, axis=0), axis=1))
        metrics = {'path_length': path_length, 'execution_time': exec_time, 'success': True}

        if visualize:
            plt.figure(figsize=(6, 6))
            for obs in obstacles:
                plt.gca().add_patch(plt.Rectangle((obs[0], obs[1]), obs[2]-obs[0], obs[3]-obs[1],
                                                  color='red', alpha=0.5))
            plt.plot(path_np[:, 0], path_np[:, 1], '-b', linewidth=2, label=selected_algorithm)
            plt.scatter(start[0], start[1], c='g', label='Start')
            plt.scatter(goal[0], goal[1], c='r', label='Goal')
            plt.legend()
            plt.axis("equal")
            plt.grid(True)
            plt.title(f"{selected_algorithm} Pathfinding")
            plt.show(block=False)
            plt.pause(0.5)
            plt.close()

        return path_np, metrics


# =====================================================================
# For Direct Execution (Testing)
# =====================================================================
def main():
    """Run a quick backend comparison and print/save summary."""
    backend = PathfindingBackend()

    start = [1, 1]
    goal = [18, 18]
    obstacles = [[5, 5, 7, 7], [10, 10, 12, 12], [15, 5, 17, 7]]

    results = {}
    for algo_name in backend.algorithms.keys():
        print(f"\nRunning {algo_name}...")
        _, metrics = backend.execute_algorithm(algo_name, start, goal, obstacles, visualize=False)
        results[algo_name] = metrics
        print(f"Metrics: {metrics}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = f"backend_report_{timestamp}.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        for algo_name, metrics in results.items():
            f.write(f"{algo_name}: {metrics}\n")

    print(f"\nSaved backend summary to {out_file}")


if __name__ == "__main__":
    main()

