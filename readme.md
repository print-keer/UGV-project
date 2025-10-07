# Advanced Robot Pathfinding Algorithm Comparison System

A comprehensive system for comparing multiple pathfinding algorithms with real-time visualization and performance analysis.

## Features

### Algorithms Implemented
1. **DWA (Dynamic Window Approach)** - Real-time obstacle avoidance
2. **A* with SLAM** - Optimal pathfinding with uncertainty handling
3. **RRT with SLAM** - Rapidly-exploring random trees with mapping
4. **GAT Pathfinder** - Graph Attention Networks for neural pathfinding
5. **Dijkstra** - Classic shortest path algorithm
6. **PRM (Probabilistic Roadmap)** - Sampling-based planning
7. **Hybrid A*** - Vehicle-aware pathfinding with kinematic constraints

### Environments
- **Simple Obstacles** - Basic scattered obstacles
- **Complex Maze** - Multi-corridor maze environment
- **Cluttered Space** - Highly dense obstacle field
- **Dynamic Obstacles** - Moving obstacles simulation
- **Multi-Level Terrain** - Varying obstacle density levels

### Key Features
- **Real-time Visualization** - Watch algorithms solve paths live
- **Speed Control** - Adjust animation speed (0.1x to 5x)
- **Performance Metrics** - Comprehensive algorithm comparison
- **SLAM Integration** - Realistic sensor uncertainty simulation
- **Interactive Controls** - Easy algorithm and environment selection
- **Detailed Reports** - JSON export of performance data

## Installation

1. Install dependencies:
\`\`\`bash
python scripts/install_dependencies.py
\`\`\`

2. Run the comparison system:
\`\`\`bash
python main.py
\`\`\`

## Usage

### Quick Start
1. Launch the application
2. Select an environment (e.g., "Simple")
3. Select an algorithm (e.g., "A* + SLAM")
4. Click "Start" to watch the algorithm solve the path
5. Use "Compare All" to test all algorithms on the current environment
6. Click "Generate Report" for detailed performance analysis

### Controls
- **Algorithm Buttons** - Select individual algorithms to test
- **Environment Buttons** - Choose different test scenarios
- **Start/Stop** - Control algorithm execution
- **Compare All** - Run all algorithms on current environment
- **Speed Slider** - Adjust visualization speed
- **Generate Report** - Create comprehensive performance report

### Performance Metrics
- **Execution Time** - How long the algorithm takes to find a path
- **Path Length** - Total distance of the found path
- **Nodes Explored** - Number of search nodes examined
- **Success Rate** - Whether a valid path was found
- **Smoothness** - Path curvature and direction changes
- **SLAM Confidence** - Uncertainty handling quality (for SLAM algorithms)

## Algorithm Details

### DWA (Dynamic Window Approach)
- Real-time reactive planning
- Excellent for dynamic environments
- Considers robot dynamics and constraints
- Fast execution but may not find optimal paths

### A* with SLAM
- Optimal pathfinding with uncertainty
- Handles sensor noise and mapping errors
- Good balance of optimality and realism
- Slower than DWA but more reliable

### RRT with SLAM
- Probabilistic exploration
- Good for complex environments
- Handles high-dimensional spaces well
- Path quality varies with sampling

### GAT Pathfinder
- Neural network-based planning
- Learns from training data
- Can adapt to different environments
- Requires training but fast inference

### Dijkstra
- Guaranteed optimal solution
- Systematic exploration
- Slower than A* but comprehensive
- Good baseline for comparison

### PRM (Probabilistic Roadmap)
- Pre-computed roadmap approach
- Efficient for multiple queries
- Good for static environments
- Setup cost amortized over multiple paths

### Hybrid A*
- Vehicle-aware pathfinding
- Considers kinematic constraints
- Realistic for car-like robots
- More complex but physically feasible paths

## Performance Analysis

The system provides detailed performance analysis including:

- **Individual Algorithm Stats** - Per-algorithm performance metrics
- **Environment Comparison** - How algorithms perform across different scenarios
- **Best Performer Identification** - Fastest, shortest path, most reliable algorithms
- **Environment Difficulty Ranking** - Which environments are most challenging
- **Comprehensive Reports** - JSON export for further analysis

## Customization

### Adding New Algorithms
1. Create new algorithm class in `algorithms/` directory
2. Implement `find_path(start, goal, obstacles, slam_data=None)` method
3. Return `(path, metrics)` tuple
4. Add to `algorithms` dictionary in `main.py`

### Adding New Environments
1. Add generation function to `EnvironmentGenerator`
2. Return dictionary with `obstacles`, `start`, `goal`, `bounds`
3. Add to `environments` dictionary in `main.py`

### Modifying Metrics
1. Update algorithm implementations to return additional metrics
2. Modify `PerformanceAnalyzer` to handle new metrics
3. Update visualization code to display new metrics

## Technical Requirements

- Python 3.7+
- NumPy for numerical computations
- Matplotlib for visualization
- NetworkX for graph algorithms
- Scikit-learn for machine learning utilities
- PyTorch for neural network algorithms
- Torch Geometric for graph neural networks

## Output Files

- **Performance Reports** - `pathfinding_report_YYYYMMDD_HHMMSS.json`
- **Algorithm Logs** - Console output with real-time performance data
- **Visualization Screenshots** - Can be saved from matplotlib interface

## Troubleshooting

### Common Issues
1. **Import Errors** - Run `python scripts/install_dependencies.py`
2. **Slow Performance** - Reduce environment complexity or algorithm iterations
3. **Memory Issues** - Limit number of algorithms tested simultaneously
4. **Visualization Problems** - Update matplotlib and check display settings

### Performance Tips
- Use "Simple" environment for initial testing
- Adjust speed slider for better visualization
- Run individual algorithms before "Compare All"
- Generate reports after completing comparisons

## Future Enhancements

Potential improvements and extensions:
- 3D pathfinding algorithms
- Multi-robot coordination
- Real robot integration
- Advanced SLAM algorithms
- Machine learning-based optimization
- Real-time obstacle detection
- Path smoothing algorithms
- Energy-efficient pathfinding
