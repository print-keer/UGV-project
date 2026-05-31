# Navigation Foundation

This document describes the first implementation milestone for the UGV project.

## Scope

This milestone implements the Person 1 navigation foundation only:

- simulation-first development
- mock occupancy grids
- A* shortest-path planning
- ROS2 package scaffolding
- shared Person 1 interface contracts
- unit tests and a runnable demo

Not included yet:

- live LiDAR ingestion
- motor control
- physical robot movement
- threat-aware path weighting
- live use of generated ROS2 message types

## ROS2 packages

- `mapping`: mock map loading and occupancy-grid publishing scaffold
- `path_planner`: planner core, cost model, and planner pipeline scaffold
- `navigation`: path consumption and navigation-status scaffold
- `mission_controller`: orchestration entrypoint for the Person 1 pipeline
- `autonomy_interfaces`: shared Person 1 data contracts used across packages
- `autonomy_msgs`: typed ROS2 `.msg` definitions for the Person 1 topic layer

## Occupancy grid format

Grid values follow the theory documents:

- `0`: free
- `1`: obstacle
- `2`: unknown

Unknown cells are traversable in this milestone, but they incur an extra cost so
future risk-aware logic can evolve without changing the planner interface.

## Person 1 pipeline contract

The current simulation-first flow now mirrors the intended node boundaries:

- `mapping` publishes an occupancy-grid-shaped contract
- `mission_controller` issues a mission goal
- `path_planner` returns planned path and planner status
- `navigation` consumes the path and returns navigation status

Current contracts are plain Python dataclasses rather than custom ROS messages,
which keeps milestone two lightweight while still freezing the integration seam.

The demo layer now also includes an in-process topic bus so the Person 1 flow can
exercise publish/subscribe style behavior and replanning before real ROS2 topic
wiring is introduced.

## ROS2 topic bridge

The current ROS2 wrapper nodes now publish and subscribe on the agreed topic
names using `std_msgs/String` as a temporary transport layer for the Person 1
contracts:

- `/mapping/occupancy_grid`
- `/mission/goal`
- `/planner/path`
- `/planner/status`
- `/navigation/status`
- `/navigation/replan_request`

The payloads are serialized versions of the shared dataclass contracts. This
keeps the topic wiring real in ROS2 while deferring custom `.msg` definitions to
a later step.

## Typed ROS2 messages

The repo now includes a dedicated `autonomy_msgs` package with typed message
definitions for:

- occupancy grid
- mission goal
- planned path
- planner status
- navigation status
- replan request

The Python nodes still use the JSON-over-`std_msgs/String` bridge in this repo
so the code remains runnable outside a full ROS2 build environment. Once the
workspace is built in ROS2 Humble, these typed messages can replace the string
transport without changing the higher-level Person 1 contracts or topic names.

The ROS wrapper nodes are now transport-aware: they automatically prefer the
generated `autonomy_msgs` message classes when available in the sourced ROS2
workspace, and otherwise fall back to `std_msgs/String` with the same topic
names and payload contracts.

## Phase 1 baseline hardening

The Person 1 stack now includes a first round of ROS2 runtime hardening:

- critical state topics use durable QoS for late subscribers
- mission goal is republished on a fixed cadence
- mock occupancy grids are republished continuously
- planner and navigation outputs are easier to inspect after startup
- a single launch file is available for bringing up the full Person 1 stack

Recommended launch command on a ROS2 Humble machine:

```bash
ros2 launch mission_controller person1_stack.launch.py
```

## Phase 2 simulated world updates

The mapping layer now supports dynamic obstacle scenarios on top of the mock
grids. This lets Person 1 exercise a more realistic loop:

- publish a baseline occupancy grid
- inject deterministic obstacle updates over time
- advance map revisions
- trigger planner recalculation against the updated world state

This is still simulation-first and grid-based, but it moves the stack closer to
live navigation behavior than one-shot static maps.

## Phase 3 replanning and failure policy

The Person 1 stack now carries richer planner and navigation status so runtime
behavior is easier to reason about:

- planner status includes start, goal, and map revision context
- navigation status includes current path length
- replan requests can carry the map revision that triggered them
- dynamic mission execution records terminal state and recovery behavior

The current failure policy is conservative: if a dynamic update produces a
`no_path` condition, the stack reports the blocked state and holds position
rather than fabricating motion past an unsolved route.

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

After `colcon build`, the generated typed messages for `autonomy_msgs` should be
available to Python and C++ nodes inside the workspace environment.
