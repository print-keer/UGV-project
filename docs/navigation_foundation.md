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

## Phase 4 navigation execution

The navigation layer now simulates waypoint-by-waypoint mission execution on top
of the planner output:

- path acceptance is separated from goal completion
- waypoint progress is recorded as an execution timeline
- mission execution can distinguish reached-goal vs blocked-route outcomes
- orchestration reports how many progress steps were taken for each map revision

This is still simulation-first and does not command real motors yet, but it
turns navigation from a static path handoff into a mission-progress layer.

## Phase 5 visualization and simulation support

The Person 1 stack now includes an RViz-friendly visualization bridge:

- the live Person 1 topics are converted into standard RViz message types
- occupancy grids are republished as `nav_msgs/OccupancyGrid`
- planned routes are republished as `nav_msgs/Path`
- goal and navigation state are exposed through pose and marker topics
- a dedicated RViz config and launch file are included for visualization-first debugging

Recommended visualization launch on a ROS2 Humble machine:

```bash
ros2 launch mission_controller person1_visualization.launch.py use_rviz:=true
```

## Phase 6 simulated sensor integration

The mapping side now supports a first sensor-ingestion layer without waiting for
real hardware:

- mock maps can define LiDAR-like obstacle observations
- mock maps can define ultrasonic-like near-field obstacle observations
- a sensor fusion layer applies those observations onto the occupancy grid
- map revisions can now come from simulated sensor inputs as well as scripted map changes

This is the software half of Phase 6. It prepares the Person 1 stack to accept
real hardware-ready sensor streams later, while letting us test the
sensor-to-map-to-replan loop today.

## Phase 7 hardware-facing sensor adapters

The mapping package now includes real-sensor-facing adapter scaffolds for the
next Person 1 step:

- `lidar_adapter_node` subscribes to `sensor_msgs/LaserScan`
- `ultrasonic_adapter_node` subscribes to `sensor_msgs/Range`
- both convert incoming readings into the shared `SensorObservation` contract
- both publish onto the internal Person 1 sensor topics:
  - `/sensors/lidar_obstacles`
  - `/sensors/ultrasonic_obstacles`

This means the planner side still sees the exact same contract whether the
input came from simulation or from live ROS2 sensor messages.

Recommended hardware-facing launch on a ROS2 Humble machine:

```bash
ros2 launch mission_controller person1_hardware_sensors.launch.py
```

You can now also override the real hardware input topics at launch time, for example:

```bash
ros2 launch mission_controller person1_hardware_sensors.launch.py scan_topic:=/scan ultrasonic_topic:=/ultrasonic/range
```

Default adapter parameter files are now included for:

- `lidar_adapter_defaults.yaml`
- `ultrasonic_adapter_defaults.yaml`

The LiDAR adapter also now supports:

- scan decimation with `scan_stride`
- angle offset correction with `angle_offset_rad`
- automatic fallback to the incoming scan `frame_id` when `source_map` is left empty

## Phase 8 motion-command handoff

The navigation side now includes a first motion-command seam for Person 1:

- `navigation_node` converts planned paths into `MotionCommand` messages
- commands are published on `/motion/command`
- a `motion_adapter_node` subscribes to those commands as the placeholder
  hardware-facing handoff
- the path follower now emits:
  - `step_to_cell` commands while progressing through waypoints
  - `hold_position` when no path exists
  - `emergency_stop` when a blocked waypoint is encountered
  - `stop_at_goal` when the route finishes

This does not drive real motors yet, but it freezes the contract between
navigation logic and the future motor-control layer.

The adapter layer now also translates `MotionCommand` into a hardware-facing
motor API shape with:

- `mode`
- `target_row`
- `target_col`
- `forward_speed`
- `turn_rate`
- `left_wheel_speed`
- `right_wheel_speed`
- `brake`
- `emergency_stop`

That keeps the eventual motor driver boundary simple even before real hardware
driver code exists.

## Phase 9 motor controller stub

The Person 1 stack now also includes a dedicated motor-side ROS2 package:

- `motor_controller_node` subscribes to `/motion/command`
- it converts each command into the motor-control API shape
- a `MotorDriverStub` applies that command in software-only form
- the stub publishes `MotorStatus` on `/motor/status`

This gives Person 1 a proper motor-control handoff package before real GPIO,
PWM, or driver-hat code is connected.

The motor handoff is now differential-drive aware, so the software can express
movement in terms that are much closer to real left/right wheel control.

## Phase 10 mission execution state machine

The mission controller now maintains a lightweight mission state machine and
publishes `/mission/state`.

It reacts differently to:

- planner success vs no-path
- navigation following vs blocked vs reached-goal
- motor hold vs active tracking vs emergency stop

This gives Person 1 an actual mission-level behavior layer instead of only raw
component status logs.

## Phase 11 mission action policy

The mission controller now also reacts to mission-state persistence:

- repeated `holding` can trigger goal republish
- repeated `blocked` can trigger replanning requests
- `emergency_stop` latches mission halt

This is still intentionally conservative, but it turns mission control into an
active coordinator instead of a passive observer.

## Phase 12 live monitoring workflow

The stack now includes a dedicated mission monitor node for ROS2 bring-up:

- `monitor_node` subscribes to:
  - `/mission/state`
  - `/planner/status`
  - `/navigation/status`
  - `/motion/command`
  - `/motor/status`
- it prints compact snapshots of the full Person 1 execution loop
- a new launch file is available:

```bash
ros2 launch mission_controller person1_observe.launch.py
```

This makes it much easier to inspect the whole autonomy loop on a real ROS2
machine without manually echoing many topics in separate terminals.

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
