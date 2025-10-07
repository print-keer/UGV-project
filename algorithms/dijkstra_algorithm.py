"""
Dijkstra's Algorithm for pathfinding
Classic shortest path algorithm with guaranteed optimality
"""

import numpy as np
import heapq
from collections import defaultdict
import math

class DijkstraPathfinder:
    def __init__(self):
        self.grid_resolution = 0.5
        self.robot_radius = 0.5
        
    def find_path(self, start, goal, obstacles, slam_data=None):
        """Find path using Dijkstra's algorithm"""
        # Convert to grid coordinates
        grid_start = self.world_to_grid(start)
        grid_goal = self.world_to_grid(goal)
        
        # Create occupancy grid
        occupancy_grid = self.create_occupancy_grid(obstacles)
        
        # Dijkstra's algorithm
        distances = defaultdict(lambda: float('inf'))
        distances[grid_start] = 0
        came_from = {}
        priority_queue = [(0, grid_start)]
        visited = set()
        
        explored_nodes = 0
        
        while priority_queue:
            current_dist, current = heapq.heappop(priority_queue)
            
            if current in visited:
                continue
                
            visited.add(current)
            explored_nodes += 1
            
            if current == grid_goal:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(self.grid_to_world(current))
                    current = came_from[current]
                path.append(start)
                path.reverse()
                
                metrics = {
                    'path_length': self.calculate_path_length(path),
                    'nodes_explored': explored_nodes,
                    'success_rate': 1.0,
                    'smoothness': self.calculate_smoothness(path),
                    'optimality': 1.0  # Dijkstra guarantees optimal solution
                }
                
                return np.array(path), metrics
            
            # Explore neighbors
            for neighbor in self.get_neighbors(current):
                if neighbor in visited or not self.is_valid_cell(neighbor, occupancy_grid):
                    continue
                
                new_distance = current_dist + self.distance(current, neighbor)
                
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    came_from[neighbor] = current
                    heapq.heappush(priority_queue, (new_distance, neighbor))
        
        # No path found
        metrics = {
            'path_length': float('inf'),
            'nodes_explored': explored_nodes,
            'success_rate': 0.0,
            'smoothness': float('inf'),
            'optimality': 0.0
        }
        
        return None, metrics
    
    def world_to_grid(self, pos):
        """Convert world coordinates to grid coordinates"""
        return (int(pos[0] / self.grid_resolution), int(pos[1] / self.grid_resolution))
    
    def grid_to_world(self, grid_pos):
        """Convert grid coordinates to world coordinates"""
        return np.array([grid_pos[0] * self.grid_resolution, grid_pos[1] * self.grid_resolution])
    
    def create_occupancy_grid(self, obstacles):
        """Create occupancy grid"""
        occupancy_grid = {}
        
        # Mark obstacle cells
        for obstacle in obstacles:
            grid_pos = self.world_to_grid(obstacle)
            # Add robot radius buffer
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if dx*dx + dy*dy <= 4:  # Circular buffer
                        cell = (grid_pos[0] + dx, grid_pos[1] + dy)
                        occupancy_grid[cell] = True
        
        return occupancy_grid
    
    def is_valid_cell(self, cell, occupancy_grid):
        """Check if cell is valid (not occupied)"""
        return not occupancy_grid.get(cell, False)
    
    def get_neighbors(self, cell):
        """Get neighboring cells (8-connected)"""
        x, y = cell
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                neighbors.append((x + dx, y + dy))
        return neighbors
    
    def distance(self, cell1, cell2):
        """Calculate distance between cells"""
        dx = cell1[0] - cell2[0]
        dy = cell1[1] - cell2[1]
        return math.sqrt(dx*dx + dy*dy)
    
    def calculate_path_length(self, path):
        """Calculate total path length"""
        if len(path) < 2:
            return 0
        return np.sum(np.linalg.norm(np.diff(path, axis=0), axis=1))
    
    def calculate_smoothness(self, path):
        """Calculate path smoothness"""
        if len(path) < 3:
            return 0
        
        angles = []
        for i in range(1, len(path) - 1):
            v1 = path[i] - path[i-1]
            v2 = path[i+1] - path[i]
            
            norm1, norm2 = np.linalg.norm(v1), np.linalg.norm(v2)
            if norm1 > 0 and norm2 > 0:
                cos_angle = np.clip(np.dot(v1, v2) / (norm1 * norm2), -1, 1)
                angle = np.arccos(cos_angle)
                angles.append(angle)
        
        return np.std(angles) if angles else 0
