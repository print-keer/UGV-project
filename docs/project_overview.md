# Project Overview

This document gives a shareable summary of the UGV repository so multiple team
members can start working in parallel without having to reverse-engineer the
theory documents first.

## What this repository is for

The repo is intended to become the central implementation base for a modular
autonomous UGV with three primary engineering lanes:

- autonomy and navigation
- AI perception and threat classification
- hardware assembly and platform enablement

The system is being developed in stages, beginning with simulation-first
validation and then expanding toward ROS2 integration and physical deployment.

## Current milestone

The current repo includes the basic shared structure, the Person 1 navigation
foundation, and the first Person 2 perception scaffold:

- mock occupancy-grid maps
- A* shortest-path planner
- ROS2 package scaffolding for mapping, planning, navigation, and mission flow
- pure Python inference and threat-classification helpers
- optional runtime image inference path for OpenCV and YOLO
- ROS2 package scaffolding for `vision` and `threat_detection`
- simulation demo for sample maps
- automated baseline tests

This milestone deliberately does not include live sensors, motors, live camera
streaming between ROS nodes, custom ROS messages, or threat-aware route
weighting yet.

## Recommended team ownership

- Person 1 should work mainly in `autonomy/`, `ros2_ws/src/navigation/`,
  `ros2_ws/src/path_planner/`, `ros2_ws/src/mapping/`,
  `ros2_ws/src/mission_controller/`, `ros2_ws/src/autonomy_interfaces/`,
  `ros2_ws/src/autonomy_msgs/`, and `simulation/`
- Person 2 should work mainly in `ai/`, `ros2_ws/src/vision/`, and
  `ros2_ws/src/threat_detection/`
- Person 3 should work mainly in `firmware/`, `hardware/`, and hardware-facing
  setup docs and checklists

This keeps the repo modular and reduces merge conflicts while the subsystems are
still evolving independently.

In the updated split, Person 1 and Person 2 own the code implementation.
Person 3 owns the physical robot assembly, Raspberry Pi bring-up, wiring,
mounting, and hardware readiness for software testing.

## Shared technical direction

- ROS2 target: Humble
- primary language at this stage: Python
- path-planning baseline: A*
- map representation: occupancy grid with `0`, `1`, and `2`
- simulation-first workflow before hardware testing
- future integration point: threat-aware path selection with separate cost logic

## Useful starting points

- [README.md](/D:/Projects/UGV_FINAL/UGV-project/README.md): project-level overview
- [revised_execution_plan.md](/D:/Projects/UGV_FINAL/UGV-project/docs/revised_execution_plan.md): updated role split, phases, dependencies, and handoffs
- [navigation_foundation.md](/D:/Projects/UGV_FINAL/UGV-project/docs/navigation_foundation.md): current milestone details
- [ugv_master_implementation.md](/D:/Projects/UGV_FINAL/UGV-project/Theory/ugv_master_implementation.md): master project theory
- [ugv_work_division.md](/D:/Projects/UGV_FINAL/UGV-project/Theory/ugv_work_division.md): team-based work split
