"""
A* Algorithm with SLAM Integration
Combines A* pathfinding with Simultaneous Localization and Mapping
"""

import numpy as np
import heapq
from collections import defaultdict
import math

class AStarSLAM:
    def __init__(self):
        self.grid_resolution = 0.5
        self.robot_radius = 0.5
        self.slam_uncertainty = 0.1
        
    def find_path(self, start, goal, obstacles, slam_data=None):
        """Find path using A* with SLAM integration"""
        # Convert to grid coordinates
        grid_start = self.world_to_grid(start)
        grid_goal = self.world_to_grid(goal)
        
        # Create occupancy grid with SLAM uncertainty
        occupancy_grid = self.create_occupancy_grid(obstacles, slam_data)
        
        # A* algorithm
        open_set = [(0, grid_start)]
        came_from = {}
        g_score = defaultdict(lambda: float('inf'))
        g_score[grid_start] = 0
        f_score = defaultdict(lambda: float('inf'))
        f_score[grid_start] = self.heuristic(grid_start, grid_goal)
        
        explored_nodes = 0
        path_nodes = []
        
        while open_set:
            current_f, current = heapq.heappop(open_set)
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
                    'slam_confidence': slam_data['confidence'] if slam_data else 1.0
                }
                
                return np.array(path), metrics
            
            # Explore neighbors
            for neighbor in self.get_neighbors(current):
                if not self.is_valid_cell(neighbor, occupancy_grid):
                    continue
                
                # SLAM-adjusted cost
                slam_cost = self.get_slam_cost(neighbor, slam_data) if slam_data else 0
                tentative_g = g_score[current] + self.distance(current, neighbor) + slam_cost
                
                if tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, grid_goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        # No path found
        metrics = {
            'path_length': float('inf'),
            'nodes_explored': explored_nodes,
            'success_rate': 0.0,
            'smoothness': float('inf'),
            'slam_confidence': slam_data['confidence'] if slam_data else 1.0
        }
        
        return None, metrics
    
    def world_to_grid(self, pos):
        """Convert world coordinates to grid coordinates"""
        return (int(pos[0] / self.grid_resolution), int(pos[1] / self.grid_resolution))
    
    def grid_to_world(self, grid_pos):
        """Convert grid coordinates to world coordinates"""
        return np.array([grid_pos[0] * self.grid_resolution, grid_pos[1] * self.grid_resolution])
    
    def create_occupancy_grid(self, obstacles, slam_data):
        """Create occupancy grid with SLAM uncertainty"""
        # Determine grid bounds
        all_points = obstacles
        if len(all_points) == 0:
            return {}
        
        min_x = int(np.min(all_points[:, 0]) / self.grid_resolution) - 5
        max_x = int(np.max(all_points[:, 0]) / self.grid_resolution) + 5
        min_y = int(np.min(all_points[:, 1]) / self.grid_resolution) - 5
        max_y = int(np.max(all_points[:, 1]) / self.grid_resolution) + 5
        
        occupancy_grid = {}
        
        # Mark obstacle cells
        for obstacle in obstacles:
            grid_pos = self.world_to_grid(obstacle)
            # Add robot radius buffer
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if dx*dx + dy*dy <= 4:  # Circular buffer
                        cell = (grid_pos[0] + dx, grid_pos[1] + dy)
                        occupancy_grid[cell] = 1.0
        
        # Add SLAM uncertainty
        if slam_data:
            for cell in occupancy_grid:
                uncertainty = slam_data.get('uncertainty', {}).get(cell, 0)
                occupancy_grid[cell] = min(1.0, occupancy_grid[cell] + uncertainty)
        
        return occupancy_grid
    
    def is_valid_cell(self, cell, occupancy_grid):
        """Check if cell is valid (not occupied)"""
        return occupancy_grid.get(cell, 0) < 0.5
    
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
    
    def heuristic(self, cell, goal):
        """A* heuristic (Euclidean distance)"""
        return self.distance(cell, goal)
    
    def get_slam_cost(self, cell, slam_data):
        """Get additional cost based on SLAM uncertainty"""
        if not slam_data:
            return 0
        uncertainty = slam_data.get('uncertainty', {}).get(cell, 0)
        return uncertainty * 2.0  # Penalty for uncertain areas
    
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
            angle = np.arccos(np.clip(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)), -1, 1))
            angles.append(angle)
        
        return np.std(angles) if angles else 0
