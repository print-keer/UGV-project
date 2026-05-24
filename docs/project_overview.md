# Project Overview

This document gives a shareable summary of the UGV repository so multiple team
members can start working in parallel without having to reverse-engineer the
theory documents first.

## What this repository is for

The repo is intended to become the central implementation base for a modular
autonomous UGV with three primary engineering lanes:

- autonomy and navigation
- AI perception and threat classification
- hardware and embedded integration

The system is being developed in stages, beginning with simulation-first
validation and then expanding toward ROS2 integration and physical deployment.

## Current milestone

The current repo includes the basic shared structure plus the Person 1
navigation foundation:

- mock occupancy-grid maps
- A* shortest-path planner
- ROS2 package scaffolding for mapping, planning, navigation, and mission flow
- simulation demo for sample maps
- automated baseline tests

This milestone deliberately does not include live sensors, motors, AI
inference, or threat-aware route weighting yet.

## Recommended team ownership

- Person 1 should work mainly in `autonomy/`, `ros2_ws/src/navigation/`,
  `ros2_ws/src/path_planner/`, `ros2_ws/src/mapping/`, and `simulation/`
- Person 2 should work mainly in `ai/`, `ros2_ws/src/vision/`, and
  `ros2_ws/src/threat_detection/`
- Person 3 should work mainly in `firmware/`, `hardware/`, and
  `ros2_ws/src/hardware_interface/`

This keeps the repo modular and reduces merge conflicts while the subsystems are
still evolving independently.

## Shared technical direction

- ROS2 target: Humble
- primary language at this stage: Python
- path-planning baseline: A*
- map representation: occupancy grid with `0`, `1`, and `2`
- simulation-first workflow before hardware testing
- future integration point: threat-aware path selection with separate cost logic

## Useful starting points

- [README.md](/D:/Projects/UGV_FINAL/UGV-project/README.md): project-level overview
- [navigation_foundation.md](/D:/Projects/UGV_FINAL/UGV-project/docs/navigation_foundation.md): current milestone details
- [ugv_master_implementation.md](/D:/Projects/UGV_FINAL/UGV-project/Theory/ugv_master_implementation.md): master project theory
- [ugv_work_division.md](/D:/Projects/UGV_FINAL/UGV-project/Theory/ugv_work_division.md): team-based work split
