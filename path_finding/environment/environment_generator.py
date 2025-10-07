"""
Environment Generator
Creates various test environments for pathfinding algorithms
"""

import numpy as np
import random

class EnvironmentGenerator:
    def __init__(self):
        self.environments = {
            'simple_obstacles': self.generate_simple_obstacles,
            'complex_maze': self.generate_complex_maze,
            'cluttered_space': self.generate_cluttered_space,
            'dynamic_obstacles': self.generate_dynamic_obstacles,
            'multi_level_terrain': self.generate_multi_level_terrain
        }
    
    def generate_environment(self, env_type):
        """Generate environment based on type"""
        if env_type in self.environments:
            return self.environments[env_type]()
        else:
            return self.generate_simple_obstacles()
    
    def generate_simple_obstacles(self):
        """Generate simple obstacle environment"""
        obstacles = np.array([
            [2, 2], [3, 2], [4, 2],
            [6, 4], [7, 4], [8, 4],
            [10, 6], [11, 6], [12, 6],
            [5, 8], [6, 8], [7, 8],
            [14, 10], [15, 10], [16, 10]
        ])
        
        return {
            'obstacles': obstacles,
            'start': np.array([0, 0]),
            'goal': np.array([18, 12]),
            'bounds': [0, 20, 0, 15],
            'description': 'Simple scattered obstacles'
        }
    
    def generate_complex_maze(self):
        """Generate maze-like environment"""
        obstacles = []
        
        # Vertical walls
        for x in [5, 10, 15]:
            for y in range(0, 12):
                if y not in [3, 6, 9]:  # Gaps in walls
                    obstacles.append([x, y])
        
        # Horizontal walls
        for y in [3, 6, 9]:
            for x in range(0, 20):
                if x not in [2, 7, 12, 17]:  # Gaps in walls
                    obstacles.append([x, y])
        
        # Additional maze complexity
        for i in range(30):
            x = random.randint(0, 19)
            y = random.randint(0, 11)
            obstacles.append([x, y])
        
        return {
            'obstacles': np.array(obstacles),
            'start': np.array([1, 1]),
            'goal': np.array([18, 10]),
            'bounds': [0, 20, 0, 12],
            'description': 'Complex maze with multiple corridors'
        }
    
    def generate_cluttered_space(self):
        """Generate highly cluttered environment"""
        obstacles = []
        
        # Random clutter
        for _ in range(100):
            x = random.uniform(2, 18)
            y = random.uniform(2, 13)
            obstacles.append([x, y])
        
        # Ensure path exists by creating corridors
        # Horizontal corridor
        for x in np.arange(0, 20, 0.5):
            y = 7.5
            # Remove nearby obstacles
            obstacles = [obs for obs in obstacles if np.linalg.norm([obs[0] - x, obs[1] - y]) > 1.0]
        
        # Vertical corridors
        for y in np.arange(0, 15, 0.5):
            for x in [5, 15]:
                obstacles = [obs for obs in obstacles if np.linalg.norm([obs[0] - x, obs[1] - y]) > 1.0]
        
        return {
            'obstacles': np.array(obstacles),
            'start': np.array([1, 7.5]),
            'goal': np.array([19, 7.5]),
            'bounds': [0, 20, 0, 15],
            'description': 'Highly cluttered space with narrow passages'
        }
    
    def generate_dynamic_obstacles(self):
        """Generate environment with dynamic obstacles"""
        # Static obstacles
        static_obstacles = np.array([
            [3, 3], [4, 3], [5, 3],
            [8, 6], [9, 6], [10, 6],
            [12, 9], [13, 9], [14, 9]
        ])
        
        # Dynamic obstacles (moving)
        dynamic_obstacles = np.array([
            [6, 2], [7, 2],  # Moving horizontally
            [2, 8], [2, 9],  # Moving vertically
            [16, 5], [17, 5] # Moving diagonally
        ])
        
        return {
            'obstacles': static_obstacles,
            'dynamic_obstacles': dynamic_obstacles,
            'start': np.array([0, 0]),
            'goal': np.array([18, 12]),
            'bounds': [0, 20, 0, 15],
            'description': 'Environment with moving obstacles'
        }
    
    def generate_multi_level_terrain(self):
        """Generate multi-level terrain environment"""
        obstacles = []
        
        # Create "terrain levels" using obstacle density
        # Level 1: Low obstacles
        for x in range(0, 7):
            for y in range(0, 5):
                if random.random() < 0.2:
                    obstacles.append([x, y])
        
        # Level 2: Medium obstacles
        for x in range(7, 14):
            for y in range(5, 10):
                if random.random() < 0.4:
                    obstacles.append([x, y])
        
        # Level 3: High obstacles
        for x in range(14, 20):
            for y in range(10, 15):
                if random.random() < 0.6:
                    obstacles.append([x, y])
        
        # Create bridges between levels
        bridge_points = [
            [6, 4], [7, 5],   # Bridge 1-2
            [13, 9], [14, 10] # Bridge 2-3
        ]
        
        # Remove obstacles at bridge points
        for bridge in bridge_points:
            obstacles = [obs for obs in obstacles if np.linalg.norm([obs[0] - bridge[0], obs[1] - bridge[1]]) > 1.5]
        
        return {
            'obstacles': np.array(obstacles),
            'start': np.array([1, 1]),
            'goal': np.array([18, 13]),
            'bounds': [0, 20, 0, 15],
            'description': 'Multi-level terrain with varying obstacle density'
        }
