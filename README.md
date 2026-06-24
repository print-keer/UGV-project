# UGV Project

This repository is the shared engineering base for a modular autonomous
Unmanned Ground Vehicle (UGV) prototype. The project is being developed as a
multi-person system with separate workstreams for autonomy, AI perception, and
hardware assembly and platform enablement.

## Project objective

The target system is a simulation-first, ROS2-based UGV that can:

- navigate autonomously toward a goal
- build and consume occupancy-style environment maps
- compute shortest paths through a grid world
- detect and classify harmful versus harmless objects
- trigger alerts while continuing mission execution
- evolve toward threat-aware route selection

The long-term architecture follows the theory documents already in the repo:

- ROS2-centered modular node design
- A* for baseline path planning
- occupancy-grid mapping for navigation
- YOLOv8n for embedded-friendly object detection
- later fusion of navigation, perception, and threat-aware costing

## Current repository status

The current repository now includes the shared scaffold, Person 1 navigation
foundation, and the first Person 2 perception foundation so the team can keep
working in parallel.

Implemented now:

- full top-level project scaffold
- ROS2 Python package layout under `ros2_ws/src/`
- mock occupancy grid loading
- A* shortest-path planning core
- simulation-first planner demo
- unit-tested baseline planner behavior
- pure Python AI inference and threat-classification scaffolding
- optional OpenCV and Ultralytics runtime inference path
- ROS2 package scaffolding for vision and threat-detection nodes
- starter docs for team onboarding

Planned next:

- typed ROS2 message alignment between autonomy and perception
- integration of AI detections into mission and navigation logic
- live LiDAR and ultrasonic software integration for Person 1
- real camera and trained-model runtime integration for Person 2
- hardware-connected validation on the assembled robot
- threat-aware route scoring
- simulation and hardware integration

## Team workstreams

- Person 1: autonomy software, mapping, path planning, navigation, mission logic, robotics integration
- Person 2: dataset, training, inference, threat classification, camera pipeline, alert logic
- Person 3: Raspberry Pi bring-up, wiring, mounting, power, chassis assembly, hardware readiness

A short collaboration guide is available in
[docs/project_overview.md](/D:/Projects/UGV_FINAL/UGV-project/docs/project_overview.md).
The updated execution roadmap is in
[docs/revised_execution_plan.md](/D:/Projects/UGV_FINAL/UGV-project/docs/revised_execution_plan.md).

## Repository layout

- `autonomy/`: autonomy-oriented non-ROS project structure and future assets
- `ai/`: dataset, training, inference, models, and threat classification
- `firmware/`: motor, sensor, and PWM control structure
- `hardware/`: hardware platform notes and physical integration assets
- `ros2_ws/src/`: ROS2 packages for navigation, mapping, planning, and mission control
- `simulation/`: mock maps and future Gazebo simulation assets
- `configs/`: shared project configuration
- `logs/`: logs and run artifacts
- `tests/`: Python tests for milestone one logic
- `docs/`: project documentation
- `deployment/`: deployment and packaging structure

## Local development

The current autonomy and AI foundation modules are largely plain Python so they
can be tested without ROS2. The ROS2 package wrappers are scaffolded for ROS2
Humble with `rclpy`.

See [docs/navigation_foundation.md](/D:/Projects/UGV_FINAL/UGV-project/docs/navigation_foundation.md) for setup,
package roles, test commands, and demo usage. The Person 2 foundation is
described in [docs/ai_foundation.md](/D:/Projects/UGV_FINAL/UGV-project/docs/ai_foundation.md).
