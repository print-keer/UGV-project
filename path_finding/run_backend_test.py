from backend_runner import PathfindingBackend

# Initialize the backend
backend = PathfindingBackend()

# Define test environment
start = [1, 1]
goal = [18, 18]
obstacles = [
    [5, 5, 7, 7],
    [10, 10, 12, 12],
    [15, 5, 17, 7]
]

# Run all algorithms and visualize
for algo in backend.algorithms.keys():
    print(f"\nRunning {algo}...")
    path, metrics = backend.execute_algorithm(algo, start, goal, obstacles, visualize=True)
    print(f"Metrics for {algo}: {metrics}")
