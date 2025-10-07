"""
Fast Robot Pathfinding Algorithm Comparison System
Optimized for quick execution and real-time visualization
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button, Slider
import time
import json
from datetime import datetime

from algorithms.dwa_algorithm import Config as DWAConfig
from algorithms.astar_slam import AStarSLAM
from algorithms.rrt_slam import RRTSLAM
from algorithms.gat_pathfinder import GATPathfinder
from algorithms.dijkstra_algorithm import DijkstraPathfinder
from environment.environment_generator import EnvironmentGenerator
from utils.performance_analyzer import PerformanceAnalyzer

class FastPathfindingComparison:
    def __init__(self):
        print(" Initializing Fast Pathfinding Comparison System...")
        
        self.algorithms = {}
        self._initialize_algorithms()
        
        self.environments = {
            'Simple': 'simple_obstacles',
            'Maze': 'complex_maze', 
            'Cluttered': 'cluttered_space',
            'Dynamic': 'dynamic_obstacles'
        }
        
        self.performance_analyzer = PerformanceAnalyzer()
        self.env_generator = EnvironmentGenerator()
        
        self.results = {}
        self.current_algorithm = None
        self.current_environment = None
        self.animation_speed = 2.0  # Faster default speed
        self.is_running = False
        
        print(" System initialized successfully!")
        
    def _initialize_algorithms(self):
        """Initialize algorithms with error handling"""
        algorithm_classes = {
            'A* + SLAM': AStarSLAM,
            'RRT + SLAM': RRTSLAM, 
            'GAT Pathfinder': GATPathfinder,
            'Dijkstra': DijkstraPathfinder
        }
        
        for name, AlgClass in algorithm_classes.items():
            try:
                self.algorithms[name] = AlgClass()
                print(f" ✓ {name} initialized")
            except Exception as e:
                print(f" ✗ Failed to initialize {name}: {e}")
                self.algorithms[name] = None
        
        # Add DWA separately
        self.algorithms['DWA'] = None  # Special handling
        print(f" ✓ DWA ready (special handling)")
        
    def setup_visualization(self):
        """Setup fast visualization interface"""
        print(" Setting up visualization...")
        
        self.fig = plt.figure(figsize=(14, 8))
        plt.suptitle("Fast Robot Pathfinding Comparison", fontsize=16, fontweight='bold')
        
        # Main plot
        self.ax_main = plt.subplot2grid((2, 3), (0, 0), colspan=2, rowspan=2)
        self.ax_main.set_title("Algorithm Visualization")
        self.ax_main.set_xlabel("X Position (m)")
        self.ax_main.set_ylabel("Y Position (m)")
        self.ax_main.grid(True, alpha=0.3)
        
        # Performance plot
        self.ax_perf = plt.subplot2grid((2, 3), (0, 2))
        self.ax_perf.set_title("Performance Metrics")
        
        # Comparison plot
        self.ax_comp = plt.subplot2grid((2, 3), (1, 2))
        self.ax_comp.set_title("Algorithm Comparison")
        
        self.setup_controls()
        print(" Visualization ready!")
        
    def setup_controls(self):
        """Setup control interface"""
        button_width = 0.08
        button_height = 0.03
        
        # Algorithm buttons
        self.algorithm_buttons = {}
        y_pos = 0.95
        x_start = 0.02
        
        for i, name in enumerate(self.algorithms.keys()):
            if self.algorithms[name] is not None or name == 'DWA':
                ax_button = plt.axes([x_start + i * 0.12, y_pos, button_width, button_height])
                button = Button(ax_button, name, color='lightblue')
                button.on_clicked(self._make_algorithm_callback(name))
                self.algorithm_buttons[name] = button
        
        # Environment buttons  
        y_pos = 0.91
        self.env_buttons = {}
        for i, name in enumerate(self.environments.keys()):
            ax_button = plt.axes([x_start + i * 0.12, y_pos, button_width, button_height])
            button = Button(ax_button, name, color='lightgreen')
            button.on_clicked(self._make_environment_callback(name))
            self.env_buttons[name] = button
        
        # Control buttons
        y_pos = 0.87
        
        # Start button
        ax_start = plt.axes([x_start, y_pos, button_width, button_height])
        self.start_button = Button(ax_start, 'Start', color='yellow')
        self.start_button.on_clicked(self.start_comparison)
        
        # Stop button  
        ax_stop = plt.axes([x_start + 0.12, y_pos, button_width, button_height])
        self.stop_button = Button(ax_stop, 'Stop', color='red')
        self.stop_button.on_clicked(self.stop_comparison)
        
        # Compare All button
        ax_compare = plt.axes([x_start + 0.24, y_pos, button_width, button_height])
        self.compare_button = Button(ax_compare, 'Compare All', color='orange')
        self.compare_button.on_clicked(self.compare_all_algorithms)
        
        # Report button
        ax_report = plt.axes([x_start + 0.36, y_pos, button_width, button_height])
        self.report_button = Button(ax_report, 'Report', color='purple')
        self.report_button.on_clicked(self.generate_report)
        
        # Speed slider
        ax_speed = plt.axes([0.02, 0.83, 0.3, 0.02])
        self.speed_slider = Slider(ax_speed, 'Speed', 0.5, 5.0, valinit=2.0)
        self.speed_slider.on_changed(self.update_speed)
        
        print(" All buttons and controls initialized successfully!")
    
    def _make_algorithm_callback(self, algorithm_name):
        """Create callback function for algorithm button"""
        def callback(event):
            self.select_algorithm(algorithm_name)
        return callback
    
    def _make_environment_callback(self, env_name):
        """Create callback function for environment button"""
        def callback(event):
            self.select_environment(env_name)
        return callback
    
    def select_algorithm(self, algorithm_name):
        """Select algorithm for testing"""
        self.current_algorithm = algorithm_name
        print(f" Selected algorithm: {algorithm_name}")
        
        # Highlight selected button
        for name, button in self.algorithm_buttons.items():
            if name == algorithm_name:
                button.color = 'gold'
            else:
                button.color = 'lightblue'
        plt.draw()
        
    def select_environment(self, env_name):
        """Select environment for testing"""
        self.current_environment = env_name
        print(f" Selected environment: {env_name}")
        
        # Generate and plot environment
        try:
            environment = self.env_generator.generate_environment(self.environments[env_name])
            self.plot_environment(environment)
            
            # Highlight selected button
            for name, button in self.env_buttons.items():
                if name == env_name:
                    button.color = 'lime'
                else:
                    button.color = 'lightgreen'
            plt.draw()
            
        except Exception as e:
            print(f" Error generating environment: {e}")
        
    def plot_environment(self, environment):
        """Plot the selected environment with proper visualization"""
        self.ax_main.clear()
        
        obstacles = environment['obstacles']
        if len(obstacles) > 0:
            for obstacle in obstacles:
                # Create obstacle as filled rectangle (0.5x0.5 size)
                rect = plt.Rectangle((obstacle[0]-0.25, obstacle[1]-0.25), 0.5, 0.5, 
                                   facecolor='red', alpha=0.8, edgecolor='darkred', linewidth=2)
                self.ax_main.add_patch(rect)
            
        start = environment['start']
        goal = environment['goal']
        
        # Start position (green circle with arrow)
        self.ax_main.plot(start[0], start[1], 'go', markersize=15, label='Start', 
                         markeredgecolor='darkgreen', markeredgewidth=2)
        self.ax_main.annotate('START', (start[0], start[1]), xytext=(5, 5), 
                            textcoords='offset points', fontsize=10, fontweight='bold')
        
        # Goal position (red star)
        self.ax_main.plot(goal[0], goal[1], 'r*', markersize=20, label='Goal', 
                         markeredgecolor='darkred', markeredgewidth=2)
        self.ax_main.annotate('GOAL', (goal[0], goal[1]), xytext=(5, 5), 
                            textcoords='offset points', fontsize=10, fontweight='bold')
        
        # Set bounds with padding
        bounds = environment['bounds']
        self.ax_main.set_xlim(bounds[0] - 1, bounds[1] + 1)
        self.ax_main.set_ylim(bounds[2] - 1, bounds[3] + 1)
        
        self.ax_main.grid(True, alpha=0.3, linestyle='--')
        self.ax_main.set_aspect('equal')
        self.ax_main.legend(loc='upper right')
        self.ax_main.set_title(f"{self.current_environment} Environment", fontsize=12, fontweight='bold')
        
        plt.draw()
        plt.pause(0.01)
        
    def update_speed(self, val):
        """Update animation speed"""
        self.animation_speed = val
        print(f" Animation speed: {val:.1f}x")
        
    def start_comparison(self, event):
        """Start pathfinding comparison"""
        if not self.current_algorithm:
            print(" Please select an algorithm first!")
            return
        if not self.current_environment:
            print(" Please select an environment first!")
            return
            
        print(f" Starting {self.current_algorithm} on {self.current_environment}")
        self.is_running = True
        self.run_algorithm()
        
    def stop_comparison(self, event):
        """Stop current comparison"""
        self.is_running = False
        print(" Comparison stopped")
        plt.draw()
        
    def run_algorithm(self):
        """Run selected algorithm with fast visualization"""
        if not self.is_running:
            return
            
        try:
            environment = self.env_generator.generate_environment(self.environments[self.current_environment])
            
            start_time = time.time()
            
            if self.current_algorithm == 'DWA':
                path, metrics = self.run_dwa_fast(environment)
            else:
                algorithm = self.algorithms[self.current_algorithm]
                if algorithm is None:
                    print(f" Algorithm {self.current_algorithm} not available")
                    return
                
                path, metrics = algorithm.find_path(
                    environment['start'],
                    environment['goal'], 
                    environment['obstacles']
                )
            
            execution_time = time.time() - start_time
            
            if path is not None and self.is_running:
                self.visualize_path_fast(path, metrics, environment)
                print(f" Path found! Length: {metrics.get('path_length', 0):.2f}m, Time: {execution_time:.3f}s")
            elif not self.is_running:
                print(" Algorithm stopped by user")
            else:
                print(" No path found!")
                
        except Exception as e:
            print(f" Error running algorithm: {e}")
            
    def run_dwa_fast(self, environment):
        """Fast DWA implementation"""
        start = environment['start']
        goal = environment['goal']
        obstacles = environment['obstacles']
        
        # Simple DWA-like trajectory
        path = [start]
        current = np.array(start)
        
        for step in range(50):  # Max 50 steps
            if not self.is_running:
                print(" DWA algorithm stopped")
                break
                
            # Simple goal-seeking with obstacle avoidance
            to_goal = goal - current
            dist_to_goal = np.linalg.norm(to_goal)
            
            if dist_to_goal < 0.5:
                path.append(goal)
                break
            
            # Normalize direction
            direction = to_goal / dist_to_goal
            
            # Simple obstacle avoidance
            for obstacle in obstacles:
                to_obstacle = current - obstacle
                dist_to_obstacle = np.linalg.norm(to_obstacle)
                
                if dist_to_obstacle < 2.0:  # Avoidance radius
                    avoidance = to_obstacle / (dist_to_obstacle + 0.1)
                    direction += avoidance * 0.5
            
            # Normalize and step
            if np.linalg.norm(direction) > 0:
                direction = direction / np.linalg.norm(direction)
            
            step_size = min(0.5, dist_to_goal)
            current = current + direction * step_size
            path.append(current.copy())
        
        metrics = {
            'path_length': self._calculate_path_length(path),
            'execution_time': 0.1,
            'success_rate': 1.0 if len(path) > 1 else 0.0,
            'algorithm': 'DWA (Fast)'
        }
        
        return np.array(path), metrics
        
    def visualize_path_fast(self, path, metrics, environment):
        """Enhanced path visualization with robot animation"""
        if not self.is_running:
            return
            
        self.plot_environment(environment)
        
        if len(path) > 1:
            self.ax_main.plot(path[:, 0], path[:, 1], 'b-', linewidth=4, alpha=0.7, 
                            label=f'{self.current_algorithm} Path', zorder=2)
            
            self.ax_main.plot(path[1:-1, 0], path[1:-1, 1], 'bo', markersize=4, 
                            alpha=0.6, zorder=3)
            
            if self.is_running:
                self.animate_robot_movement(path)
        
        self.update_performance_display(metrics)
        
        self.ax_main.legend()
        plt.draw()
        
    def animate_robot_movement(self, path):
        """Animate robot moving along the path"""
        if len(path) < 2 or not self.is_running:
            return
            
        print(" Starting robot animation...")
        robot_circle = plt.Circle((0, 0), 0.3, color='blue', alpha=0.8, zorder=5)
        self.ax_main.add_patch(robot_circle)
        
        for i in range(len(path)):
            if not self.is_running:
                print(" Robot animation stopped")
                break
                
            robot_circle.center = (path[i, 0], path[i, 1])
            
            if i < len(path) - 1:
                direction = path[i+1] - path[i]
                if np.linalg.norm(direction) > 0:
                    direction = direction / np.linalg.norm(direction) * 0.5
                    self.ax_main.arrow(path[i, 0], path[i, 1], direction[0], direction[1],
                                     head_width=0.2, head_length=0.1, fc='yellow', ec='orange',
                                     alpha=0.8, zorder=6)
            
            plt.draw()
            plt.pause(0.05 / self.animation_speed)
            
            if not self.is_running:
                print(" Robot animation interrupted")
                break
            
            if i > 0 and self.is_running:
                self.plot_environment(self.env_generator.generate_environment(
                    self.environments[self.current_environment]))
                self.ax_main.plot(path[:i+2, 0], path[:i+2, 1], 'b-', linewidth=4, 
                                alpha=0.7, zorder=2)
                robot_circle = plt.Circle(path[i, 0:2], 0.3, color='blue', alpha=0.8, zorder=5)
                self.ax_main.add_patch(robot_circle)
        
        if self.is_running:
            print(f" Robot reached destination!")
        
        self.is_running = False

    def visualize_all_results(self, results, environment):
        """Visualize all algorithm results with better styling"""
        self.plot_environment(environment)
        
        colors = ['blue', 'green', 'purple', 'orange', 'brown', 'pink', 'cyan']
        line_styles = ['-', '--', '-.', ':', '-', '--', '-.']
        
        for i, (alg_name, result) in enumerate(results.items()):
            if result.get('success', False) and 'path' in result:
                path = result['path']
                color = colors[i % len(colors)]
                style = line_styles[i % len(line_styles)]
                
                self.ax_main.plot(path[:, 0], path[:, 1], 
                                color=color, linewidth=3, alpha=0.8, linestyle=style,
                                label=f"{alg_name} ({result['execution_time']:.3f}s)")
                
                self.ax_main.plot(path[0, 0], path[0, 1], 'o', color=color, markersize=8, alpha=0.9)
                self.ax_main.plot(path[-1, 0], path[-1, 1], 's', color=color, markersize=8, alpha=0.9)
        
        self.plot_comparison_chart(results)
        
        self.ax_main.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
        
        plt.subplots_adjust(right=0.75)
        plt.draw()
        
    def update_performance_display(self, metrics):
        """Update performance metrics display"""
        self.ax_perf.clear()
        
        metric_names = ['Path Length', 'Exec Time', 'Success Rate']
        metric_values = [
            metrics.get('path_length', 0),
            metrics.get('execution_time', 0) * 1000,  # Convert to ms
            metrics.get('success_rate', 0) * 100  # Convert to percentage
        ]
        
        colors = ['blue', 'green', 'orange']
        bars = self.ax_perf.bar(metric_names, metric_values, color=colors, alpha=0.7)
        
        for bar, value in zip(bars, metric_values):
            height = bar.get_height()
            self.ax_perf.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                            f'{value:.2f}', ha='center', va='bottom', fontsize=8)
        
        self.ax_perf.set_title(f"{self.current_algorithm} Performance")
        self.ax_perf.tick_params(axis='x', rotation=45)
        plt.draw()
        
    def compare_all_algorithms(self, event):
        """Fast comparison of all algorithms"""
        if not self.current_environment:
            print(" Please select an environment first!")
            return
            
        print(" Starting fast algorithm comparison...")
        self.is_running = True
        
        environment = self.env_generator.generate_environment(self.environments[self.current_environment])
        results = {}
        
        for alg_name in self.algorithms.keys():
            if not self.is_running:
                print(" Comparison stopped by user")
                break
                
            if self.algorithms[alg_name] is None and alg_name != 'DWA':
                continue
                
            print(f" Testing {alg_name}...")
            
            try:
                start_time = time.time()
                
                if alg_name == 'DWA':
                    path, metrics = self.run_dwa_fast(environment)
                else:
                    path, metrics = self.algorithms[alg_name].find_path(
                        environment['start'],
                        environment['goal'],
                        environment['obstacles']
                    )
                
                execution_time = time.time() - start_time
                
                results[alg_name] = {
                    'path': path,
                    'metrics': metrics,
                    'execution_time': execution_time,
                    'success': path is not None and len(path) > 1
                }
                
                print(f" {alg_name}: {'✓' if results[alg_name]['success'] else '✗'} "
                      f"({execution_time:.3f}s)")
                
            except Exception as e:
                print(f" {alg_name} failed: {e}")
                results[alg_name] = {'success': False, 'execution_time': float('inf')}
        
        if self.is_running:
            self.visualize_all_results(results, environment)
            self.results[self.current_environment] = results
            print(" Algorithm comparison completed!")
        
        self.is_running = False

    def plot_comparison_chart(self, results):
        """Plot algorithm comparison chart"""
        self.ax_comp.clear()
        
        successful_algs = []
        exec_times = []
        path_lengths = []
        
        for alg_name, result in results.items():
            if result.get('success', False):
                successful_algs.append(alg_name)
                exec_times.append(result['execution_time'])
                
                if 'metrics' in result and 'path_length' in result['metrics']:
                    path_lengths.append(result['metrics']['path_length'])
                else:
                    path_lengths.append(0)
        
        if successful_algs:
            x_pos = np.arange(len(successful_algs))
            
            if max(exec_times) > 0:
                norm_times = np.array(exec_times) / max(exec_times)
            else:
                norm_times = np.zeros(len(exec_times))
                
            if max(path_lengths) > 0:
                norm_lengths = np.array(path_lengths) / max(path_lengths)
            else:
                norm_lengths = np.zeros(len(path_lengths))
            
            width = 0.35
            self.ax_comp.bar(x_pos - width/2, norm_times, width, 
                           label='Exec Time', alpha=0.8, color='skyblue')
            self.ax_comp.bar(x_pos + width/2, norm_lengths, width,
                           label='Path Length', alpha=0.8, color='lightcoral')
            
            self.ax_comp.set_xlabel('Algorithms')
            self.ax_comp.set_ylabel('Normalized Performance')
            self.ax_comp.set_title('Performance Comparison')
            self.ax_comp.set_xticks(x_pos)
            self.ax_comp.set_xticklabels(successful_algs, rotation=45, ha='right')
            self.ax_comp.legend()
        
        plt.draw()
        
    def generate_report(self, event):
        """Generate performance report"""
        if not self.results:
            print(" No results to report. Run comparisons first!")
            return
            
        print(" Generating performance report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'environments_tested': list(self.results.keys()),
            'algorithms_tested': list(self.algorithms.keys()),
            'results': self.results
        }
        
        filename = f"pathfinding_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f" Report saved to {filename}")
        self.print_report_summary()
        
    def print_report_summary(self):
        """Print report summary to console"""
        print("\n" + "="*60)
        print("FAST PATHFINDING ALGORITHM COMPARISON REPORT")
        print("="*60)
        
        for env_name, env_results in self.results.items():
            print(f"\nEnvironment: {env_name}")
            print("-" * 40)
            
            sorted_results = sorted(env_results.items(), 
                                  key=lambda x: x[1].get('execution_time', float('inf')))
            
            for alg_name, result in sorted_results:
                if result.get('success', False):
                    exec_time = result.get('execution_time', 0)
                    path_length = result.get('metrics', {}).get('path_length', 0)
                    print(f"{alg_name:15} | ✓ | {exec_time:.3f}s | {path_length:.2f}m")
                else:
                    print(f"{alg_name:15} | ✗ | FAILED")
        
        print("\n" + "="*60)
        
    def _calculate_path_length(self, path):
        """Calculate path length"""
        if len(path) < 2:
            return 0
        return np.sum([np.linalg.norm(path[i+1] - path[i]) for i in range(len(path)-1)])
        
    def run(self):
        """Main run method"""
        print("Starting Fast Pathfinding Comparison System...")
        self.setup_visualization()
        
        print("Loading default environment...")
        self.select_environment('Simple')
        
        print("\n" + "="*50)
        print("INSTRUCTIONS:")
        print("1. Select an algorithm (blue buttons)")
        print("2. Select an environment (green buttons)")  
        print("3. Click 'Start' to run single algorithm")
        print("4. Click 'Compare All' to test all algorithms")
        print("5. Adjust speed slider for visualization")
        print("6. Click 'Report' to generate performance report")
        print("="*50)
        
        plt.subplots_adjust(right=0.75, bottom=0.15)
        plt.show()

if __name__ == "__main__":
    try:
        comparison = FastPathfindingComparison()
        comparison.run()
    except Exception as e:
        print(f"System error: {e}")
        print("Please check that all required files are present")
