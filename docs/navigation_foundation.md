# Navigation Foundation

This document describes the first implementation milestone for the UGV project.

## Scope

This milestone implements the Person 1 navigation foundation only:

- simulation-first development
- mock occupancy grids
- A* shortest-path planning
- ROS2 package scaffolding
- unit tests and a runnable demo

Not included yet:

- live LiDAR ingestion
- motor control
- physical robot movement
- threat-aware path weighting
- full ROS2 message definitions

## ROS2 packages

- `mapping`: mock map loading and occupancy-grid publishing scaffold
- `path_planner`: planner core, cost model, and planner node scaffold
- `navigation`: path consumption and path-follower placeholder logic
- `mission_controller`: orchestration entrypoint for demo-style mission planning

## Occupancy grid format

Grid values follow the theory documents:

- `0`: free
- `1`: obstacle
- `2`: unknown

Unknown cells are traversable in this milestone, but they incur an extra cost so
future risk-aware logic can evolve without changing the planner interface.

## Suggested setup on a ROS2 machine

1. Install ROS2 Humble and Python tooling.
2. Create or use a Python virtual environment.
3. Install test tooling:

```bash
python -m pip install pytest
```

4. From the repo root, run tests:

```bash
python -m pytest tests
```

If you prefer or need to avoid extra packages, the test suite also runs with the
standard library:

```bash
python -m unittest discover -s tests -v
```

5. Run the simulation demo:

```bash
python simulation/run_planner_demo.py
```

## ROS2 build notes

On a ROS2 Humble machine:

```bash
cd ros2_ws
colcon build
```

Then source the workspace and run nodes, for example:

```bash
ros2 run mission_controller mission_demo
ros2 run path_planner planner_node
```

These node entrypoints are intentionally lightweight for milestone one and are
designed to be expanded once simulated and live topics are introduced.
