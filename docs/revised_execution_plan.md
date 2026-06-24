# Revised Execution Plan

This document is the updated source of truth for how the UGV project should be
executed after clarifying team roles.

The most important change is this:

- Person 1 and Person 2 own the complete code implementation
- Person 3 owns hardware assembly and platform enablement

That means the software system is split across two engineering lanes, while the
third lane prepares the physical robot so the software can later connect to real
devices safely and predictably.

## Team Roles

### Person 1 - Autonomy, Robotics Software & Integration

Person 1 owns the robotics software stack.

Scope:

- ROS2 architecture
- mapping
- path planning
- navigation
- mission control
- occupancy-grid updates
- LiDAR software ingestion
- ultrasonic software ingestion
- sensor fusion for navigation
- motion-command interfaces
- software integration with real hardware topics later

Main output:

- a working autonomy pipeline that can accept maps, goals, sensor inputs, and
  AI detections and produce navigation decisions

### Person 2 - AI & Vision Software

Person 2 owns the perception software stack.

Scope:

- dataset creation
- labeling
- YOLO training
- camera software pipeline
- inference runtime
- harmful/harmless classification
- alert logic
- ROS2 detection publishing
- optimization for embedded deployment

Main output:

- a working perception pipeline that can accept camera frames and publish
  structured detections and threat labels

### Person 3 - Hardware Assembly & Platform Enablement

Person 3 owns the physical robot preparation.

Scope:

- Raspberry Pi setup
- chassis assembly
- sensor mounting
- motor mounting
- power setup
- cable routing
- wiring validation
- interface enablement on the Pi
- hardware documentation
- bench-level readiness checks

Main output:

- a physically assembled and powered robot that is ready for the software team
  to connect and test

## Ownership by Directory

### Person 1

- `autonomy/`
- `ros2_ws/src/navigation/`
- `ros2_ws/src/path_planner/`
- `ros2_ws/src/mapping/`
- `ros2_ws/src/mission_controller/`
- `ros2_ws/src/autonomy_interfaces/`
- `ros2_ws/src/autonomy_msgs/`
- `simulation/`
- `configs/`
- `tests/` for autonomy-side tests

### Person 2

- `ai/`
- `ros2_ws/src/vision/`
- `ros2_ws/src/threat_detection/`
- model, dataset, and inference assets
- `tests/` for AI-side tests

### Person 3

- `hardware/`
- `firmware/` for hardware notes, bring-up references, and device setup assets
- hardware-facing docs and checklists under `docs/`

## Working Rule

Until final integration, each person should stay mostly within their own area.

This reduces merge conflicts and keeps responsibilities clear:

- Person 1 builds and validates robotics software
- Person 2 builds and validates AI software
- Person 3 prepares and validates physical hardware readiness

## Revised Project Roadmap

## Phase 0 - Shared Foundation

Goal:
Create the shared repo structure, documentation, interfaces, and simulation
baseline.

Owner:
Primarily Person 1, with documentation support for the whole team.

Status in this repo:

- already established

Deliverables:

- repo scaffold
- ROS2 workspace structure
- planning foundation
- shared docs
- initial interfaces

## Phase 1 - Person 1 Navigation Foundation

Goal:
Prove simulation-first shortest-path planning and mission flow before touching
real sensors or motors.

Owner:
Person 1

Deliverables:

- occupancy-grid contract
- mission goal contract
- planner output contract
- A* planner
- planner tests
- ROS2 topic flow for mapping, planning, navigation, and mission control
- simulation demo

Success check:

- planner works on mock maps
- nodes publish/subscribe correctly
- tests pass

## Phase 2 - Person 2 Perception Foundation

Goal:
Build the first end-to-end AI perception pipeline independent of navigation.

Owner:
Person 2

Deliverables:

- dataset structure
- labeling rules
- first training run
- camera ingestion pipeline
- inference node
- harmful/harmless output contract
- alert message contract

Success check:

- camera frames can be processed
- detections can be published in ROS2
- harmful and harmless outputs are distinguishable

## Phase 3 - Hardware Readiness

Goal:
Prepare the real UGV platform so the code team has something stable to connect
to.

Owner:
Person 3

Deliverables:

- Raspberry Pi configured
- sensors mounted
- motors mounted
- power system stable
- wiring documented
- pin mapping documented
- hardware checklist completed

Success check:

- Pi boots reliably
- interfaces are enabled
- devices are physically connected and recognized
- the robot is safe for bench testing

## Phase 4 - Real Sensor Software Integration

Goal:
Replace simulated sensor inputs with real LiDAR and ultrasonic software inputs.

Owner:
Person 1

Needs from Person 3 first:

- powered Pi
- mounted sensors
- wiring map
- confirmed device connectivity

Deliverables:

- LiDAR ingestion node or adapter
- ultrasonic ingestion node or adapter
- occupancy-grid update pipeline from real readings
- fusion logic updates
- test procedures for real sensor data

Success check:

- real sensor data reaches ROS2
- mapping updates from live readings
- planner reacts to live map changes

## Phase 5 - Real Camera AI Integration

Goal:
Replace offline or mock vision inputs with the real camera pipeline.

Owner:
Person 2

Needs from Person 3 first:

- mounted camera
- enabled camera interface
- stable physical mounting

Deliverables:

- real camera capture pipeline
- inference on live frames
- detection publishing in ROS2
- harmful/harmless output validation

Success check:

- live camera frames reach the inference node
- detections publish reliably
- alert logic works on live inputs

## Phase 6 - Autonomy + AI Fusion

Goal:
Connect Person 1 and Person 2 systems so navigation can use AI results during
mission execution.

Owners:
Person 1 and Person 2 together

Deliverables:

- stable detection message contract
- integration of AI results into navigation decision inputs
- initial threat-aware path-cost design
- end-to-end autonomy plus perception test flow

Success check:

- navigation continues while AI runs
- harmful detections can influence mission logic or route scoring
- no blocking or unstable cross-dependency between the two stacks

## Phase 7 - Motion Control and Physical Navigation

Goal:
Move from planning-only autonomy into real robot motion.

Primary owner:
Person 1

Support needed:

- Person 3 for motor wiring readiness and physical safety checks

Deliverables:

- motion command interface
- motor-control software hookup
- stop/replan behavior
- goal-progress tracking on the real robot

Success check:

- robot can move in a controlled way
- robot can stop safely
- robot can follow simple planned paths in physical tests

## Phase 8 - Full Mission Validation

Goal:
Validate the complete system in realistic test scenarios.

Owners:
All three, with Person 1 and Person 2 leading the code validation.

Deliverables:

- map test scenarios
- harmful/harmless object scenarios
- alert verification
- path-planning verification
- integration logs
- issue list for final fixes

Success check:

- robot reaches target
- obstacles are avoided
- harmful and harmless objects are classified correctly
- alerts trigger correctly
- system remains stable through repeated runs

## Handoff Points

These are the most important team dependencies.

### Handoff 1 - Person 3 to Person 1

Person 3 provides:

- mounted LiDAR and ultrasonic sensors
- wiring details
- Pi interface status
- bench-test readiness

Person 1 then uses that to connect real sensor software.

### Handoff 2 - Person 3 to Person 2

Person 3 provides:

- mounted camera
- camera interface enabled
- stable physical positioning

Person 2 then uses that to connect the real perception pipeline.

### Handoff 3 - Person 2 to Person 1

Person 2 provides:

- detection message format
- harmful/harmless output definitions
- alert output behavior

Person 1 then uses that to integrate AI results into autonomy decisions.

### Handoff 4 - Person 1 to Full Team

Person 1 provides:

- integrated navigation stack
- planner behavior
- motion command interface
- test harness for full mission flow

That becomes the backbone used during final system validation.

## Dependency Summary

### Person 1 depends on:

- Person 3 for real hardware readiness
- Person 2 for AI detection outputs during fusion

### Person 2 depends on:

- Person 3 for real camera readiness
- Person 1 only for final integration contracts, not for initial model work

### Person 3 depends on:

- Person 1 and Person 2 to clarify connector, topic, and runtime needs before
  final bench testing

## Recommended Immediate Next Work

### Person 1

- continue autonomy-side software integration
- move from simulation contracts toward live sensor-ready interfaces
- prepare the motion-command layer
- maintain the motor-controller software seam for later hardware hookup

### Person 2

- define the ROS2 detection contract
- prepare dataset and training structure
- build the first live or mock inference node

### Person 3

- finish assembly checklist
- document pin mapping and wiring
- verify Pi interfaces and power stability

## Final Plain-English Summary

The project is now best understood like this:

- Person 1 builds the robot brain for movement
- Person 2 builds the robot brain for seeing and judging objects
- Person 3 builds the robot body and gets the electronics ready

Then:

- Person 3 makes the hardware usable
- Person 2 makes the camera intelligence usable
- Person 1 connects movement, sensing, and mission behavior into one robot

That is the cleanest way to divide the work without gaps or overlap.
