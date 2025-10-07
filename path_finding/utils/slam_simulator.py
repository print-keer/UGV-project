"""
SLAM Simulator
Simulates SLAM data for algorithms that require localization and mapping
"""

import numpy as np
import random

class SLAMSimulator:
    def __init__(self):
        self.sensor_range = 5.0
        self.sensor_noise = 0.1
        self.map_resolution = 0.5
        
    def initialize_slam(self, environment):
        """Initialize SLAM data for environment"""
        obstacles = environment['obstacles']
        bounds = environment['bounds']
        
        # Create uncertainty map
        uncertainty_map = self.generate_uncertainty_map(obstacles, bounds)
        
        # Simulate sensor readings
        sensor_data = self.simulate_sensor_readings(environment['start'], obstacles)
        
        slam_data = {
            'uncertainty_map': uncertainty_map,
            'sensor_data': sensor_data,
            'confidence': self.calculate_overall_confidence(uncertainty_map),
            'map_quality': random.uniform(0.7, 0.95),  # Simulated map quality
            'localization_error': random.uniform(0.05, 0.2)  # Simulated localization error
        }
        
        return slam_data
    
    def generate_uncertainty_map(self, obstacles, bounds):
        """Generate uncertainty map based on obstacle visibility"""
        uncertainty_map = {}
        
        # Create grid
        x_min, x_max, y_min, y_max = bounds
        
        for x in np.arange(x_min, x_max, self.map_resolution):
            for y in np.arange(y_min, y_max, self.map_resolution):
                grid_pos = (int(x / self.map_resolution), int(y / self.map_resolution))
                
                # Calculate uncertainty based on distance to nearest obstacle
                min_dist_to_obstacle = float('inf')
                for obstacle in obstacles:
                    dist = np.linalg.norm([x - obstacle[0], y - obstacle[1]])
                    min_dist_to_obstacle = min(min_dist_to_obstacle, dist)
                
                # Higher uncertainty in areas far from obstacles (less sensor data)
                if min_dist_to_obstacle > self.sensor_range:
                    uncertainty = 0.8  # High uncertainty
                elif min_dist_to_obstacle > self.sensor_range / 2:
                    uncertainty = 0.4  # Medium uncertainty
                else:
                    uncertainty = 0.1  # Low uncertainty
                
                # Add random noise
                uncertainty += random.uniform(-0.1, 0.1)
                uncertainty = max(0, min(1, uncertainty))  # Clamp to [0, 1]
                
                uncertainty_map[grid_pos] = uncertainty
        
        return uncertainty_map
    
    def simulate_sensor_readings(self, robot_position, obstacles):
        """Simulate sensor readings from robot position"""
        sensor_readings = []
        
        # Simulate LIDAR-like sensor
        num_rays = 36  # 10-degree resolution
        
        for i in range(num_rays):
            angle = i * 2 * np.pi / num_rays
            
            # Cast ray
            ray_hit = self.cast_ray(robot_position, angle, obstacles)
            
            # Add noise
            if ray_hit is not None:
                noise = random.gauss(0, self.sensor_noise)
                noisy_distance = ray_hit['distance'] + noise
                
                sensor_readings.append({
                    'angle': angle,
                    'distance': max(0, noisy_distance),
                    'hit_point': ray_hit['hit_point']
                })
        
        return sensor_readings
    
    def cast_ray(self, start_pos, angle, obstacles):
        """Cast ray and find intersection with obstacles"""
        ray_dir = np.array([np.cos(angle), np.sin(angle)])
        
        min_distance = self.sensor_range
        hit_point = None
        
        # Check intersection with each obstacle
        for obstacle in obstacles:
            # Treat obstacle as circle with small radius
            obstacle_radius = 0.3
            
            # Ray-circle intersection
            to_obstacle = obstacle - start_pos
            proj_length = np.dot(to_obstacle, ray_dir)
            
            if proj_length > 0:  # Obstacle is in front
                closest_point = start_pos + proj_length * ray_dir
                distance_to_center = np.linalg.norm(closest_point - obstacle)
                
                if distance_to_center <= obstacle_radius:
                    # Ray hits obstacle
                    hit_distance = proj_length - np.sqrt(obstacle_radius**2 - distance_to_center**2)
                    
                    if 0 < hit_distance < min_distance:
                        min_distance = hit_distance
                        hit_point = start_pos + hit_distance * ray_dir
        
        if hit_point is not None:
            return {
                'distance': min_distance,
                'hit_point': hit_point
            }
        
        return None
    
    def calculate_overall_confidence(self, uncertainty_map):
        """Calculate overall SLAM confidence"""
        if not uncertainty_map:
            return 0.5
        
        uncertainties = list(uncertainty_map.values())
        avg_uncertainty = np.mean(uncertainties)
        
        # Convert uncertainty to confidence (inverse relationship)
        confidence = 1.0 - avg_uncertainty
        
        return max(0.1, min(0.95, confidence))
    
    def update_slam_data(self, slam_data, robot_position, obstacles):
        """Update SLAM data as robot moves (for dynamic scenarios)"""
        # Simulate new sensor readings
        new_sensor_data = self.simulate_sensor_readings(robot_position, obstacles)
        
        # Update uncertainty map (reduce uncertainty in explored areas)
        for reading in new_sensor_data:
            # Reduce uncertainty along sensor ray
            ray_points = self.get_ray_points(robot_position, reading['angle'], reading['distance'])
            
            for point in ray_points:
                grid_pos = (int(point[0] / self.map_resolution), int(point[1] / self.map_resolution))
                if grid_pos in slam_data['uncertainty_map']:
                    # Reduce uncertainty (sensor has observed this area)
                    slam_data['uncertainty_map'][grid_pos] *= 0.9
        
        # Update sensor data
        slam_data['sensor_data'] = new_sensor_data
        
        # Recalculate confidence
        slam_data['confidence'] = self.calculate_overall_confidence(slam_data['uncertainty_map'])
        
        return slam_data
    
    def get_ray_points(self, start_pos, angle, max_distance):
        """Get points along sensor ray"""
        ray_dir = np.array([np.cos(angle), np.sin(angle)])
        points = []
        
        for dist in np.arange(0, max_distance, self.map_resolution):
            point = start_pos + dist * ray_dir
            points.append(point)
        
        return points
