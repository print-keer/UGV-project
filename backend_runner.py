import numpy as np
import matplotlib.pyplot as plt
import json
import time
from datetime import datetime
import os

class SimplePathfinder:
    """Base class for pathfinding algorithms"""
    def __init__(self, name):
        self.name = name
    
    def plan_path(self, start, goal, obstacles, bounds):
        """Override in subclasses"""
        return []

class DWAPlanner(SimplePathfinder):
    """Dynamic Window Approach pathfinder"""
    def __init__(self):
        super().__init__("DWA")
        
    def plan_path(self, start, goal, obstacles, bounds):
        # Simple DWA implementation
        path = [start]
        current = np.array(start)
        goal_pos = np.array(goal)
        
        for _ in range(100):  # Max iterations
            if np.linalg.norm(current - goal_pos) < 1.0:
                break
                
            # Simple movement toward goal with obstacle avoidance
            direction = goal_pos - current
            direction = direction / (np.linalg.norm(direction) + 1e-6)
            
            # Check for obstacles and adjust direction
            next_pos = current + direction * 0.5
            
            # Simple obstacle avoidance
            for obs in obstacles:
                if (obs[0] <= next_pos[0] <= obs[2] and 
                    obs[1] <= next_pos[1] <= obs[3]):
                    # Avoid obstacle by going around
                    direction = np.array([-direction[1], direction[0]])  # Perpendicular
                    next_pos = current + direction * 0.5
                    break
            
            current = next_pos
            path.append(current.tolist())
            
        return path

class AStarPlanner(SimplePathfinder):
    """A* pathfinding algorithm"""
    def __init__(self):
        super().__init__("A*")
        
    def plan_path(self, start, goal, obstacles, bounds):
        # Simple A* implementation
        grid_size = 1.0
        start_grid = (int(start[0]/grid_size), int(start[1]/grid_size))
        goal_grid = (int(goal[0]/grid_size), int(goal[1]/grid_size))
        
        # Create obstacle grid
        obstacle_set = set()
        for obs in obstacles:
            for x in range(int(obs[0]/grid_size), int(obs[2]/grid_size) + 1):
                for y in range(int(obs[1]/grid_size), int(obs[3]/grid_size) + 1):
                    obstacle_set.add((x, y))
        
        # A* search
        open_set = [start_grid]
        came_from = {}
        g_score = {start_grid: 0}
        
        while open_set:
            current = min(open_set, key=lambda x: g_score.get(x, float('inf')) + 
                         np.linalg.norm(np.array(x) - np.array(goal_grid)))
            
            if current == goal_grid:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append([current[0] * grid_size, current[1] * grid_size])
                    current = came_from[current]
                path.append(start)
                return path[::-1]
            
            open_set.remove(current)
            
            # Check neighbors
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                if neighbor in obstacle_set:
                    continue
                    
                tentative_g = g_score[current] + np.sqrt(dx*dx + dy*dy)
                
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    if neighbor not in open_set:
                        open_set.append(neighbor)
        
        return []  # No path found

class RRTPlanner(SimplePathfinder):
    """RRT pathfinding algorithm"""
    def __init__(self):
        super().__init__("RRT")
        
    def plan_path(self, start, goal, obstacles, bounds):
        # Simple RRT implementation
        nodes = [start]
        parent = {0: None}
        
        for i in range(500):  # Max iterations
            # Random sampling
            if np.random.random() < 0.1:  # Goal bias
                rand_point = goal
            else:
                rand_point = [
                    np.random.uniform(bounds[0], bounds[1]),
                    np.random.uniform(bounds[2], bounds[3])
                ]
            
            # Find nearest node
            distances = [np.linalg.norm(np.array(node) - np.array(rand_point)) 
                        for node in nodes]
            nearest_idx = np.argmin(distances)
            nearest = nodes[nearest_idx]
            
            # Extend toward random point
            direction = np.array(rand_point) - np.array(nearest)
            distance = np.linalg.norm(direction)
            if distance > 2.0:  # Step size
                direction = direction / distance * 2.0
            
            new_point = (np.array(nearest) + direction).tolist()
            
            # Check collision
            collision = False
            for obs in obstacles:
                if (obs[0] <= new_point[0] <= obs[2] and 
                    obs[1] <= new_point[1] <= obs[3]):
                    collision = True
                    break
            
            if not collision:
                nodes.append(new_point)
                parent[len(nodes)-1] = nearest_idx
                
                # Check if reached goal
                if np.linalg.norm(np.array(new_point) - np.array(goal)) < 1.0:
                    # Reconstruct path
                    path = []
                    current_idx = len(nodes) - 1
                    while current_idx is not None:
                        path.append(nodes[current_idx])
                        current_idx = parent[current_idx]
                    return path[::-1]
        
        return []  # No path found

class DijkstraPlanner(SimplePathfinder):
    """Dijkstra pathfinding algorithm"""
    def __init__(self):
        super().__init__("Dijkstra")
        
    def plan_path(self, start, goal, obstacles, bounds):
        # Similar to A* but without heuristic
        grid_size = 1.0
        start_grid = (int(start[0]/grid_size), int(start[1]/grid_size))
        goal_grid = (int(goal[0]/grid_size), int(goal[1]/grid_size))
        
        # Create obstacle grid
        obstacle_set = set()
        for obs in obstacles:
            for x in range(int(obs[0]/grid_size), int(obs[2]/grid_size) + 1):
                for y in range(int(obs[1]/grid_size), int(obs[3]/grid_size) + 1):
                    obstacle_set.add((x, y))
        
        # Dijkstra search
        unvisited = {start_grid}
        distances = {start_grid: 0}
        came_from = {}
        
        while unvisited:
            current = min(unvisited, key=lambda x: distances.get(x, float('inf')))
            
            if current == goal_grid:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append([current[0] * grid_size, current[1] * grid_size])
                    current = came_from[current]
                path.append(start)
                return path[::-1]
            
            unvisited.remove(current)
            
            # Check neighbors
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                if neighbor in obstacle_set:
                    continue
                    
                new_distance = distances[current] + 1
                
                if new_distance < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_distance
                    came_from[neighbor] = current
                    unvisited.add(neighbor)
        
        return []  # No path found

class EnvironmentGenerator:
    """Generate test environments"""
    
    def generate_simple_environment(self):
        return {
            'start': [1, 1],
            'goal': [18, 18],
            'obstacles': [
                [5, 5, 7, 7],
                [10, 10, 12, 12],
                [15, 5, 17, 7]
            ],
            'bounds': [0, 20, 0, 20]
        }
    
    def generate_maze_environment(self):
        return {
            'start': [1, 1],
            'goal': [18, 18],
            'obstacles': [
                [0, 5, 15, 6],
                [5, 0, 6, 10],
                [10, 8, 20, 9],
                [8, 12, 9, 20],
                [12, 0, 13, 12]
            ],
            'bounds': [0, 20, 0, 20]
        }
    
    def generate_cluttered_environment(self):
        obstacles = []
        np.random.seed(42)  # For reproducibility
        for _ in range(15):
            x = np.random.uniform(2, 18)
            y = np.random.uniform(2, 18)
            w = np.random.uniform(0.5, 2)
            h = np.random.uniform(0.5, 2)
            obstacles.append([x, y, x+w, y+h])
        
        return {
            'start': [1, 1],
            'goal': [18, 18],
            'obstacles': obstacles,
            'bounds': [0, 20, 0, 20]
        }

class PerformanceAnalyzer:
    """Analyze algorithm performance"""
    
    def calculate_metrics(self, path, obstacles, execution_time):
        if not path or len(path) < 2:
            return {
                'execution_time': execution_time,
                'path_length': float('inf'),
                'smoothness': 0,
                'obstacle_clearance': 0
            }
        
        # Calculate path length
        path_length = 0
        for i in range(1, len(path)):
            path_length += np.linalg.norm(np.array(path[i]) - np.array(path[i-1]))
        
        # Calculate smoothness (sum of angle changes)
        smoothness = 0
        if len(path) > 2:
            for i in range(1, len(path)-1):
                v1 = np.array(path[i]) - np.array(path[i-1])
                v2 = np.array(path[i+1]) - np.array(path[i])
                if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
                    angle = np.arccos(np.clip(np.dot(v1, v2) / 
                                            (np.linalg.norm(v1) * np.linalg.norm(v2)), -1, 1))
                    smoothness += angle
        
        # Calculate minimum obstacle clearance
        min_clearance = float('inf')
        for point in path:
            for obs in obstacles:
                # Distance to rectangle
                dx = max(obs[0] - point[0], 0, point[0] - obs[2])
                dy = max(obs[1] - point[1], 0, point[1] - obs[3])
                clearance = np.sqrt(dx*dx + dy*dy)
                min_clearance = min(min_clearance, clearance)
        
        return {
            'execution_time': execution_time,
            'path_length': path_length,
            'smoothness': smoothness,
            'obstacle_clearance': min_clearance if min_clearance != float('inf') else 0
        }

class PathfindingBackend:
    def __init__(self):
        self.algorithms = {
            'DWA': DWAPlanner(),
            'A*': AStarPlanner(),
            'RRT': RRTPlanner(),
            'Dijkstra': DijkstraPlanner()
        }
        
        self.env_generator = EnvironmentGenerator()
        self.analyzer = PerformanceAnalyzer()
        self.results = {}
        
    def run_comprehensive_analysis(self):
        """Run all algorithms on all environments and generate comprehensive report"""
        print(" Starting comprehensive pathfinding analysis...")
        
        # Generate test environments
        environments = {
            'Simple': self.env_generator.generate_simple_environment(),
            'Maze': self.env_generator.generate_maze_environment(),
            'Cluttered': self.env_generator.generate_cluttered_environment()
        }
        
        # Run each algorithm on each environment
        for env_name, env_data in environments.items():
            print(f" Testing environment: {env_name}")
            self.results[env_name] = {}
            
            for algo_name, algorithm in self.algorithms.items():
                print(f" Running {algo_name} on {env_name}...")
                
                try:
                    # Time the algorithm execution
                    start_time = time.time()
                    
                    # Run pathfinding
                    path = algorithm.plan_path(
                        start=env_data['start'],
                        goal=env_data['goal'],
                        obstacles=env_data['obstacles'],
                        bounds=env_data['bounds']
                    )
                    
                    execution_time = time.time() - start_time
                    
                    # Calculate performance metrics
                    metrics = self.analyzer.calculate_metrics(
                        path, env_data['obstacles'], execution_time
                    )
                    
                    self.results[env_name][algo_name] = {
                        'path': path,
                        'metrics': metrics,
                        'success': len(path) > 0
                    }
                    
                    print(f" {algo_name} completed in {execution_time:.3f}s - {'SUCCESS' if len(path) > 0 else 'FAILED'}")
                    
                except Exception as e:
                    print(f" {algo_name} failed: {str(e)}")
                    self.results[env_name][algo_name] = {
                        'path': [],
                        'metrics': {'execution_time': float('inf'), 'path_length': float('inf')},
                        'success': False
                    }
        
        # Generate reports and visualizations
        self.generate_performance_report()
        self.create_comparative_visualizations()
        self.create_final_comparison_chart()
        
        print(" Analysis complete! Check the generated reports and visualizations.")
        
    def generate_performance_report(self):
        """Generate detailed performance report"""
        print(" Generating performance report...")
        
        # Generate human-readable report
        with open('pathfinding_analysis_report.txt', 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("ROBOT PATHFINDING ALGORITHM COMPARISON REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Calculate overall performance
            algo_performance = {}
            for algo in self.algorithms.keys():
                success_count = sum(1 for env in self.results.values() 
                                  if env.get(algo, {}).get('success', False))
                success_rate = success_count / len(self.results)
                
                avg_time = np.mean([env[algo]['metrics']['execution_time'] 
                                  for env in self.results.values() 
                                  if env.get(algo, {}).get('success', False)])
                
                avg_length = np.mean([env[algo]['metrics']['path_length'] 
                                    for env in self.results.values() 
                                    if env.get(algo, {}).get('success', False)])
                
                algo_performance[algo] = {
                    'success_rate': success_rate,
                    'avg_time': avg_time if not np.isnan(avg_time) else float('inf'),
                    'avg_length': avg_length if not np.isnan(avg_length) else float('inf')
                }
            
            # Overall Rankings
            f.write("OVERALL ALGORITHM RANKINGS:\n")
            f.write("-" * 40 + "\n")
            sorted_algos = sorted(algo_performance.items(), 
                                key=lambda x: (x[1]['success_rate'], -x[1]['avg_time']), 
                                reverse=True)
            
            for i, (algo, stats) in enumerate(sorted_algos, 1):
                f.write(f"{i}. {algo:<12} Success: {stats['success_rate']:.1%} ")
                f.write(f"Time: {stats['avg_time']:.3f}s Length: {stats['avg_length']:.2f}\n")
            f.write("\n")
            
            # Environment-specific results
            f.write("ENVIRONMENT-SPECIFIC RESULTS:\n")
            f.write("=" * 40 + "\n")
            
            for env_name, env_results in self.results.items():
                f.write(f"\n{env_name.upper()} ENVIRONMENT:\n")
                f.write("-" * 30 + "\n")
                
                for algo, result in env_results.items():
                    status = "SUCCESS" if result['success'] else "FAILED"
                    f.write(f"{algo:<12} {status:<8} ")
                    if result['success']:
                        f.write(f"Time: {result['metrics']['execution_time']:.3f}s ")
                        f.write(f"Length: {result['metrics']['path_length']:.2f}")
                    f.write("\n")
        
        print(" Text report saved as 'pathfinding_analysis_report.txt'")
        
    def create_comparative_visualizations(self):
        """Create individual environment visualizations"""
        print(" Creating comparative visualizations...")
        
        if not os.path.exists('visualizations'):
            os.makedirs('visualizations')
        
        environments = {
            'Simple': self.env_generator.generate_simple_environment(),
            'Maze': self.env_generator.generate_maze_environment(),
            'Cluttered': self.env_generator.generate_cluttered_environment()
        }
        
        for env_name, env_data in environments.items():
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Plot obstacles
            for obs in env_data['obstacles']:
                rect = plt.Rectangle((obs[0], obs[1]), obs[2]-obs[0], obs[3]-obs[1], 
                                   color='red', alpha=0.7, label='Obstacles' if obs == env_data['obstacles'][0] else "")
                ax.add_patch(rect)
            
            # Plot start and goal
            ax.plot(env_data['start'][0], env_data['start'][1], 'go', markersize=12, label='Start')
            ax.plot(env_data['goal'][0], env_data['goal'][1], 'r*', markersize=15, label='Goal')
            
            # Plot paths for each successful algorithm
            colors = ['blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
            color_idx = 0
            
            if env_name in self.results:
                for algo_name, result in self.results[env_name].items():
                    if result['success'] and len(result['path']) > 0:
                        path = np.array(result['path'])
                        ax.plot(path[:, 0], path[:, 1], 
                               color=colors[color_idx % len(colors)], 
                               linewidth=2, alpha=0.8, label=f"{algo_name}")
                        color_idx += 1
            
            ax.set_xlim(env_data['bounds'][0], env_data['bounds'][1])
            ax.set_ylim(env_data['bounds'][2], env_data['bounds'][3])
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            ax.legend()
            ax.set_title(f'Pathfinding Comparison - {env_name} Environment')
            
            plt.tight_layout()
            plt.savefig(f'visualizations/{env_name.lower()}_comparison.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        print(" Individual environment visualizations saved in 'visualizations/' folder")
        
    def create_final_comparison_chart(self):
        """Create final comprehensive comparison chart"""
        print(" Creating final comparison chart...")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        algos = list(self.algorithms.keys())
        
        # 1. Success Rate Comparison
        success_rates = []
        for algo in algos:
            success_count = sum(1 for env in self.results.values() 
                              if env.get(algo, {}).get('success', False))
            success_rates.append(success_count / len(self.results) * 100)
        
        bars1 = ax1.bar(algos, success_rates, color='skyblue', alpha=0.8)
        ax1.set_title('Success Rate by Algorithm', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Success Rate (%)')
        ax1.set_ylim(0, 100)
        
        for bar, rate in zip(bars1, success_rates):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{rate:.1f}%', ha='center', va='bottom')
        
        # 2. Average Execution Time
        avg_times = []
        for algo in algos:
            times = [env[algo]['metrics']['execution_time'] 
                    for env in self.results.values() 
                    if env.get(algo, {}).get('success', False)]
            avg_times.append(np.mean(times) if times else 0)
        
        bars2 = ax2.bar(algos, avg_times, color='lightcoral', alpha=0.8)
        ax2.set_title('Average Execution Time', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Time (seconds)')
        
        for bar, time_val in zip(bars2, avg_times):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_times)*0.01, 
                    f'{time_val:.3f}s', ha='center', va='bottom')
        
        # 3. Average Path Length
        avg_lengths = []
        for algo in algos:
            lengths = [env[algo]['metrics']['path_length'] 
                      for env in self.results.values() 
                      if env.get(algo, {}).get('success', False)]
            avg_lengths.append(np.mean(lengths) if lengths else 0)
        
        bars3 = ax3.bar(algos, avg_lengths, color='lightgreen', alpha=0.8)
        ax3.set_title('Average Path Length', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Path Length')
        
        for bar, length in zip(bars3, avg_lengths):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_lengths)*0.01, 
                    f'{length:.1f}', ha='center', va='bottom')
        
        # 4. Algorithm Comparison Table
        ax4.axis('tight')
        ax4.axis('off')
        
        table_data = []
        headers = ['Algorithm', 'Success Rate', 'Avg Time (s)', 'Avg Length']
        
        for i, algo in enumerate(algos):
            table_data.append([
                algo,
                f'{success_rates[i]:.1f}%',
                f'{avg_times[i]:.3f}',
                f'{avg_lengths[i]:.1f}'
            ])
        
        table = ax4.table(cellText=table_data, colLabels=headers, 
                         cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        ax4.set_title('Performance Summary Table', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('final_algorithm_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Final comparison chart saved as 'final_algorithm_comparison.png'")

def main():
    """Main function to run the backend analysis"""
    print("Initializing Pathfinding Backend Analysis System...")
    
    backend = PathfindingBackend()
    backend.run_comprehensive_analysis()
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print("="*60)
    print("Generated files:")
    print("- pathfinding_analysis_report.txt (human-readable report)")
    print("- final_algorithm_comparison.png (comprehensive charts)")
    print("- visualizations/ folder (individual environment comparisons)")
    print("="*60)

if __name__ == "__main__":
    main()
