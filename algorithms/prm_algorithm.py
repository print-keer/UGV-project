"""
Probabilistic Roadmap (PRM) Algorithm
Builds a roadmap of collision-free paths for efficient pathfinding
"""

import numpy as np
import networkx as nx
import random
from sklearn.neighbors import NearestNeighbors

class PRMPathfinder:
    def __init__(self):
        self.num_samples = 500
        self.connection_radius = 2.0
        self.robot_radius = 0.5
        self.roadmap = None
        
    def find_path(self, start, goal, obstacles, slam_data=None):
        """Find path using PRM algorithm"""
        # Build roadmap
        roadmap_nodes = self.build_roadmap(obstacles, start, goal)
        
        if len(roadmap_nodes) < 2:
            return self._fallback_path(start, goal, obstacles)
        
        # Create graph
        G = self.create_graph(roadmap_nodes, obstacles)
        
        # Find start and goal nodes in roadmap
        start_node = self.find_nearest_node(roadmap_nodes, start)
        goal_node = self.find_nearest_node(roadmap_nodes, goal)
        
        if start_node is None or goal_node is None:
            return self._fallback_path(start, goal, obstacles)
        
        # Find shortest path
        try:
            path_indices = nx.shortest_path(G, start_node, goal_node, weight='weight')
            path = [roadmap_nodes[i] for i in path_indices]
            
            # Smooth path
            path = self.smooth_path(path, obstacles)
            
            metrics = {
                'path_length': self.calculate_path_length(path),
                'nodes_explored': len(roadmap_nodes),
                'roadmap_size': len(roadmap_nodes),
                'success_rate': 1.0,
                'smoothness': self.calculate_smoothness(path)
            }
            
            return np.array(path), metrics
            
        except nx.NetworkXNoPath:
            return self._fallback_path(start, goal, obstacles)
    
    def build_roadmap(self, obstacles, start, goal):
        """Build probabilistic roadmap"""
        # Determine sampling bounds
        if len(obstacles) > 0:
            bounds = [
                np.min(obstacles[:, 0]) - 5, np.max(obstacles[:, 0]) + 5,
                np.min(obstacles[:, 1]) - 5, np.max(obstacles[:, 1]) + 5
            ]
        else:
            bounds = [min(start[0], goal[0]) - 5, max(start[0], goal[0]) + 5,
                     min(start[1], goal[1]) - 5, max(start[1], goal[1]) + 5]
        
        # Sample collision-free points
        roadmap_nodes = [start, goal]  # Always include start and goal
        
        attempts = 0
        while len(roadmap_nodes) < self.num_samples and attempts < self.num_samples * 3:
            # Random sampling
            sample = np.array([
                random.uniform(bounds[0], bounds[1]),
                random.uniform(bounds[2], bounds[3])
            ])
            
            # Check collision
            if self.is_collision_free_point(sample, obstacles):
                roadmap_nodes.append(sample)
            
            attempts += 1
        
        return roadmap_nodes
    
    def create_graph(self, nodes, obstacles):
        """Create graph from roadmap nodes"""
        G = nx.Graph()
        
        # Add nodes
        for i, node in enumerate(nodes):
            G.add_node(i, pos=node)
        
        # Add edges using k-nearest neighbors
        if len(nodes) > 1:
            nbrs = NearestNeighbors(n_neighbors=min(10, len(nodes)), algorithm='ball_tree').fit(nodes)
            
            for i, node in enumerate(nodes):
                distances, indices = nbrs.kneighbors([node])
                
                for j, neighbor_idx in enumerate(indices[0]):
                    if neighbor_idx != i and distances[0][j] <= self.connection_radius:
                        neighbor = nodes[neighbor_idx]
                        
                        # Check if connection is collision-free
                        if self.is_collision_free_path(node, neighbor, obstacles):
                            weight = np.linalg.norm(node - neighbor)
                            G.add_edge(i, neighbor_idx, weight=weight)
        
        return G
    
    def find_nearest_node(self, nodes, point):
        """Find nearest node to given point"""
        if not nodes:
            return None
        
        distances = [np.linalg.norm(node - point) for node in nodes]
        return np.argmin(distances)
    
    def is_collision_free_point(self, point, obstacles):
        """Check if point is collision-free"""
        for obstacle in obstacles:
            if np.linalg.norm(point - obstacle) < self.robot_radius:
                return False
        return True
    
    def is_collision_free_path(self, start_pos, end_pos, obstacles):
        """Check if path segment is collision-free"""
        # Discretize path
        distance = np.linalg.norm(end_pos - start_pos)
        num_checks = int(distance / 0.1) + 1
        
        for i in range(num_checks + 1):
            t = i / num_checks if num_checks > 0 else 0
            check_pos = start_pos + t * (end_pos - start_pos)
            
            if not self.is_collision_free_point(check_pos, obstacles):
                return False
        
        return True
    
    def smooth_path(self, path, obstacles):
        """Smooth path by removing unnecessary waypoints"""
        if len(path) < 3:
            return path
        
        smoothed = [path[0]]
        i = 0
        
        while i < len(path) - 1:
            j = len(path) - 1
            
            # Find furthest reachable point
            while j > i + 1:
                if self.is_collision_free_path(path[i], path[j], obstacles):
                    break
                j -= 1
            
            smoothed.append(path[j])
            i = j
        
        return smoothed
    
    def _fallback_path(self, start, goal, obstacles):
        """Fallback path when PRM fails"""
        path = [start, goal]
        
        metrics = {
            'path_length': np.linalg.norm(goal - start),
            'nodes_explored': 2,
            'roadmap_size': 0,
            'success_rate': 0.5,
            'smoothness': 0.0
        }
        
        return np.array(path), metrics
    
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
