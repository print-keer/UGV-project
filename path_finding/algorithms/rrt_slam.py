"""
RRT (Rapidly-exploring Random Tree) with SLAM Integration
"""

import numpy as np
import random
import math

class RRTSLAM:
    def __init__(self):
        self.max_iterations = 5000
        self.step_size = 0.5
        self.goal_threshold = 0.5
        self.robot_radius = 0.5
        
    def find_path(self, start, goal, obstacles, slam_data=None):
        """Find path using RRT with SLAM integration"""
        # Initialize tree
        tree = {0: {'pos': np.array(start), 'parent': None, 'cost': 0}}
        node_count = 1
        
        # Determine search bounds
        if len(obstacles) > 0:
            bounds = [
                np.min(obstacles[:, 0]) - 5, np.max(obstacles[:, 0]) + 5,
                np.min(obstacles[:, 1]) - 5, np.max(obstacles[:, 1]) + 5
            ]
        else:
            bounds = [-10, 20, -10, 20]
        
        goal_node = None
        iterations = 0
        
        while iterations < self.max_iterations:
            iterations += 1
            
            # Sample random point (bias towards goal)
            if random.random() < 0.1:  # 10% bias towards goal
                rand_point = np.array(goal)
            else:
                rand_point = np.array([
                    random.uniform(bounds[0], bounds[1]),
                    random.uniform(bounds[2], bounds[3])
                ])
            
            # Find nearest node
            nearest_node_id = self.find_nearest_node(tree, rand_point)
            nearest_pos = tree[nearest_node_id]['pos']
            
            # Steer towards random point
            direction = rand_point - nearest_pos
            distance = np.linalg.norm(direction)
            
            if distance > self.step_size:
                direction = direction / distance * self.step_size
            
            new_pos = nearest_pos + direction
            
            # Check collision with SLAM uncertainty
            if self.is_collision_free(nearest_pos, new_pos, obstacles, slam_data):
                # Add new node
                slam_cost = self.get_slam_cost(new_pos, slam_data) if slam_data else 0
                new_cost = tree[nearest_node_id]['cost'] + distance + slam_cost
                
                tree[node_count] = {
                    'pos': new_pos,
                    'parent': nearest_node_id,
                    'cost': new_cost
                }
                
                # Check if goal is reached
                if np.linalg.norm(new_pos - goal) < self.goal_threshold:
                    goal_node = node_count
                    break
                
                node_count += 1
        
        # Extract path
        if goal_node is not None:
            path = self.extract_path(tree, goal_node)
            path = self.smooth_path(path, obstacles, slam_data)
            
            metrics = {
                'path_length': self.calculate_path_length(path),
                'nodes_explored': node_count,
                'iterations': iterations,
                'success_rate': 1.0,
                'smoothness': self.calculate_smoothness(path),
                'slam_confidence': slam_data['confidence'] if slam_data else 1.0
            }
            
            return np.array(path), metrics
        
        # No path found
        metrics = {
            'path_length': float('inf'),
            'nodes_explored': node_count,
            'iterations': iterations,
            'success_rate': 0.0,
            'smoothness': float('inf'),
            'slam_confidence': slam_data['confidence'] if slam_data else 1.0
        }
        
        return None, metrics
    
    def find_nearest_node(self, tree, point):
        """Find nearest node in tree"""
        min_dist = float('inf')
        nearest_id = 0
        
        for node_id, node in tree.items():
            dist = np.linalg.norm(node['pos'] - point)
            if dist < min_dist:
                min_dist = dist
                nearest_id = node_id
        
        return nearest_id
    
    def is_collision_free(self, start_pos, end_pos, obstacles, slam_data):
        """Check if path segment is collision-free"""
        # Discretize path
        num_checks = int(np.linalg.norm(end_pos - start_pos) / 0.1) + 1
        
        for i in range(num_checks + 1):
            t = i / num_checks if num_checks > 0 else 0
            check_pos = start_pos + t * (end_pos - start_pos)
            
            # Check collision with obstacles
            for obstacle in obstacles:
                if np.linalg.norm(check_pos - obstacle) < self.robot_radius:
                    return False
            
            # Check SLAM uncertainty
            if slam_data:
                uncertainty = self.get_position_uncertainty(check_pos, slam_data)
                if uncertainty > 0.7:  # High uncertainty threshold
                    return False
        
        return True
    
    def get_slam_cost(self, position, slam_data):
        """Get cost based on SLAM uncertainty"""
        if not slam_data:
            return 0
        
        uncertainty = self.get_position_uncertainty(position, slam_data)
        return uncertainty * 1.5  # Cost penalty for uncertain areas
    
    def get_position_uncertainty(self, position, slam_data):
        """Get uncertainty at given position"""
        if not slam_data or 'uncertainty_map' not in slam_data:
            return 0
        
        # Simple grid-based lookup
        grid_x = int(position[0] / 0.5)
        grid_y = int(position[1] / 0.5)
        return slam_data['uncertainty_map'].get((grid_x, grid_y), 0)
    
    def extract_path(self, tree, goal_node):
        """Extract path from tree"""
        path = []
        current = goal_node
        
        while current is not None:
            path.append(tree[current]['pos'])
            current = tree[current]['parent']
        
        path.reverse()
        return path
    
    def smooth_path(self, path, obstacles, slam_data):
        """Smooth path by removing unnecessary waypoints"""
        if len(path) < 3:
            return path
        
        smoothed = [path[0]]
        i = 0
        
        while i < len(path) - 1:
            j = len(path) - 1
            
            # Find furthest reachable point
            while j > i + 1:
                if self.is_collision_free(path[i], path[j], obstacles, slam_data):
                    break
                j -= 1
            
            smoothed.append(path[j])
            i = j
        
        return smoothed
    
    def calculate_path_length(self, path):
        """Calculate total path length"""
        if len(path) < 2:
            return 0
        return np.sum([np.linalg.norm(path[i+1] - path[i]) for i in range(len(path)-1)])
    
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
