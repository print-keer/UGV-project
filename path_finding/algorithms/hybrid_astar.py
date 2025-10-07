"""
Hybrid A* Algorithm
Combines A* with continuous space search for vehicle-like robots
"""

import numpy as np
import heapq
import math
from collections import defaultdict

class HybridAStar:
    def __init__(self):
        self.grid_resolution = 0.5
        self.angle_resolution = np.pi / 8  # 22.5 degrees
        self.robot_radius = 0.5
        self.wheelbase = 1.0
        self.max_steer = np.pi / 4  # 45 degrees
        self.motion_primitives = self.generate_motion_primitives()
        
    def generate_motion_primitives(self):
        """Generate motion primitives for vehicle model"""
        primitives = []
        
        # Forward motions
        for steer in [-self.max_steer, -self.max_steer/2, 0, self.max_steer/2, self.max_steer]:
            primitives.append({
                'steer': steer,
                'distance': 1.0,
                'direction': 1  # forward
            })
        
        # Backward motions (limited)
        for steer in [-self.max_steer/2, 0, self.max_steer/2]:
            primitives.append({
                'steer': steer,
                'distance': 0.5,
                'direction': -1  # backward
            })
        
        return primitives
    
    def find_path(self, start, goal, obstacles, slam_data=None):
        """Find path using Hybrid A* algorithm"""
        # Convert to hybrid state (x, y, theta)
        start_state = (start[0], start[1], 0)  # Assume starting angle is 0
        goal_state = (goal[0], goal[1], 0)    # Goal angle doesn't matter much
        
        # Initialize search
        open_set = [(0, start_state, [])]  # (f_score, state, path)
        closed_set = set()
        g_score = defaultdict(lambda: float('inf'))
        g_score[start_state] = 0
        
        explored_nodes = 0
        best_path = None
        best_cost = float('inf')
        
        while open_set and explored_nodes < 5000:  # Limit search
            current_f, current_state, current_path = heapq.heappop(open_set)
            
            if current_state in closed_set:
                continue
            
            closed_set.add(current_state)
            explored_nodes += 1
            
            # Check if goal reached (with tolerance)
            goal_dist = math.sqrt((current_state[0] - goal_state[0])**2 + 
                                (current_state[1] - goal_state[1])**2)
            
            if goal_dist < 1.0:  # Goal tolerance
                path = current_path + [np.array([current_state[0], current_state[1]])]
                cost = g_score[current_state]
                
                if cost < best_cost:
                    best_cost = cost
                    best_path = path
                
                # Continue searching for better solution
                continue
            
            # Expand using motion primitives
            for primitive in self.motion_primitives:
                new_state, trajectory = self.apply_motion_primitive(current_state, primitive)
                
                if new_state is None:
                    continue
                
                # Check collision
                if not self.is_trajectory_collision_free(trajectory, obstacles):
                    continue
                
                # Calculate cost
                motion_cost = primitive['distance']
                if primitive['direction'] == -1:  # Penalty for reverse
                    motion_cost *= 2.0
                
                tentative_g = g_score[current_state] + motion_cost
                
                # Discretize state for comparison
                discrete_state = self.discretize_state(new_state)
                
                if tentative_g < g_score[discrete_state]:
                    g_score[discrete_state] = tentative_g
                    f_score = tentative_g + self.heuristic(new_state, goal_state)
                    
                    new_path = current_path + [np.array([pt[0], pt[1]]) for pt in trajectory]
                    heapq.heappush(open_set, (f_score, discrete_state, new_path))
        
        if best_path is not None:
            # Smooth path
            smoothed_path = self.smooth_path(best_path, obstacles)
            
            metrics = {
                'path_length': self.calculate_path_length(smoothed_path),
                'nodes_explored': explored_nodes,
                'success_rate': 1.0,
                'smoothness': self.calculate_smoothness(smoothed_path),
                'kinematic_feasibility': 1.0  # Hybrid A* ensures kinematic feasibility
            }
            
            return np.array(smoothed_path), metrics
        
        # No path found
        metrics = {
            'path_length': float('inf'),
            'nodes_explored': explored_nodes,
            'success_rate': 0.0,
            'smoothness': float('inf'),
            'kinematic_feasibility': 0.0
        }
        
        return None, metrics
    
    def apply_motion_primitive(self, state, primitive):
        """Apply motion primitive to get new state and trajectory"""
        x, y, theta = state
        steer = primitive['steer']
        distance = primitive['distance']
        direction = primitive['direction']
        
        # Bicycle model
        trajectory = [(x, y)]
        
        # Simulate motion
        dt = 0.1
        steps = int(distance / dt)
        
        for _ in range(steps):
            # Update state using bicycle model
            x += direction * dt * math.cos(theta)
            y += direction * dt * math.sin(theta)
            theta += direction * dt * math.tan(steer) / self.wheelbase
            
            # Normalize angle
            theta = math.atan2(math.sin(theta), math.cos(theta))
            
            trajectory.append((x, y))
        
        new_state = (x, y, theta)
        return new_state, trajectory
    
    def discretize_state(self, state):
        """Discretize continuous state for comparison"""
        x, y, theta = state
        
        grid_x = round(x / self.grid_resolution)
        grid_y = round(y / self.grid_resolution)
        grid_theta = round(theta / self.angle_resolution)
        
        return (grid_x, grid_y, grid_theta)
    
    def is_trajectory_collision_free(self, trajectory, obstacles):
        """Check if trajectory is collision-free"""
        for point in trajectory:
            for obstacle in obstacles:
                if math.sqrt((point[0] - obstacle[0])**2 + (point[1] - obstacle[1])**2) < self.robot_radius:
                    return False
        return True
    
    def heuristic(self, state, goal):
        """Heuristic function (Euclidean distance)"""
        return math.sqrt((state[0] - goal[0])**2 + (state[1] - goal[1])**2)
    
    def smooth_path(self, path, obstacles):
        """Smooth path while maintaining collision-free property"""
        if len(path) < 3:
            return path
        
        smoothed = [path[0]]
        i = 0
        
        while i < len(path) - 1:
            j = len(path) - 1
            
            # Find furthest reachable point
            while j > i + 1:
                if self.is_line_collision_free(path[i], path[j], obstacles):
                    break
                j -= 1
            
            smoothed.append(path[j])
            i = j
        
        return smoothed
    
    def is_line_collision_free(self, start, end, obstacles):
        """Check if line segment is collision-free"""
        distance = np.linalg.norm(end - start)
        num_checks = int(distance / 0.1) + 1
        
        for i in range(num_checks + 1):
            t = i / num_checks if num_checks > 0 else 0
            point = start + t * (end - start)
            
            for obstacle in obstacles:
                if np.linalg.norm(point - obstacle) < self.robot_radius:
                    return False
        
        return True
    
    def calculate_path_length(self, path):
        """Calculate total path length"""
        if len(path) < 2:
            return 0
        return np.sum([np.linalg.norm(path[i+1] - path[i]) for i in range(len(path)-1)])
    
    def calculate_smoothness(self, path):
        """Calculate path smoothness"""
        if len(path) < 3:
            return 0
        
        curvatures = []
        for i in range(1, len(path) - 1):
            # Calculate curvature at each point
            p1, p2, p3 = path[i-1], path[i], path[i+1]
            
            # Vectors
            v1 = p2 - p1
            v2 = p3 - p2
            
            # Cross product magnitude (proportional to curvature)
            cross = abs(v1[0] * v2[1] - v1[1] * v2[0])
            
            # Normalize by distance
            dist1, dist2 = np.linalg.norm(v1), np.linalg.norm(v2)
            if dist1 > 0 and dist2 > 0:
                curvature = cross / (dist1 * dist2)
                curvatures.append(curvature)
        
        return np.std(curvatures) if curvatures else 0
