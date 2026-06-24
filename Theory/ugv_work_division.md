# UGV Team-Based Implementation Workflow

# Military Grade Autonomous UGV - Distributed Execution Blueprint

---

# 1. Document Purpose

This document defines how a 3-member team should split the UGV project so work
can happen in parallel without confusion.

The architecture is intentionally divided so that:

- each team member can independently clone the repository
- each member can work in parallel
- Codex can execute tasks based on PERSON tags
- integration conflicts are minimized
- development stays modular and scalable

This workflow follows a practical robotics engineering approach for a student
team building one shared system.

---

# 2. Team Structure

## PERSON 1 - AUTONOMY, ROBOTICS SOFTWARE & INTEGRATION ENGINEER

Responsible for:

- ROS2 architecture
- path planning
- mapping
- navigation stack
- occupancy grid logic
- A* implementation
- replanning logic
- threat-aware route selection
- LiDAR software integration
- ultrasonic software integration
- navigation-to-motion command interfaces
- autonomy software integration across shared ROS2 topics

Primary Domain:
AUTONOMY SOFTWARE

---

## PERSON 2 - AI & VISION ENGINEER

Responsible for:

- dataset creation
- object detection
- YOLO training
- threat classification
- camera software pipeline
- inference optimization
- alert logic
- detection pipeline
- AI ROS2 publishing interfaces

Primary Domain:
AI PERCEPTION SYSTEM

---

## PERSON 3 - HARDWARE ASSEMBLY & PLATFORM ENABLEMENT

Responsible for:

- Raspberry Pi setup
- physical chassis assembly
- motor mounting
- sensor mounting
- sensor wiring
- LiDAR mounting
- ultrasonic mounting
- camera mounting
- power systems
- Raspberry Pi bring-up
- mechanical and electrical validation
- hardware debugging support
- assembly and wiring documentation

Primary Domain:
PHYSICAL PLATFORM READINESS

Not responsible for:

- ROS2 node implementation
- LiDAR ROS2 software
- ultrasonic ROS2 software
- motor-control software
- navigation code
- AI inference code

---

# 3. Global Development Strategy

## Important Rule

No member should directly modify another member's module unless the integration
phase has begun.

Each subsystem must:

- build independently
- run independently
- be testable independently

Final integration happens only after module validation.

Coding ownership should stay primarily with Person 1 and Person 2.
Person 3 supports by making sure the real robot hardware is assembled, powered,
mounted correctly, and ready for software hookup and testing.

---

# 4. Master Repository Structure

```text
UGV/
|
|-- autonomy/
|-- ai/
|-- firmware/
|-- hardware/
|-- ros2_ws/
|-- simulation/
|-- configs/
|-- logs/
|-- tests/
`-- docs/
```

---

# 5. PERSON 1 - Complete Implementation Roadmap

# PERSON 1
# ROLE: AUTONOMY, ROBOTICS SOFTWARE & INTEGRATION ENGINEER

---

# PERSON 1 - Primary Objective

Build the complete robotics autonomy software stack.

This includes:

- mapping
- navigation
- path planning
- route optimization
- collision prevention
- threat-aware routing
- LiDAR software ingestion
- ultrasonic software ingestion
- sensor fusion for navigation
- hardware-facing software integration points

---

# PERSON 1 - Directory Ownership

```text
autonomy/
ros2_ws/src/navigation/
ros2_ws/src/path_planner/
ros2_ws/src/mapping/
ros2_ws/src/mission_controller/
ros2_ws/src/autonomy_interfaces/
ros2_ws/src/autonomy_msgs/
simulation/
configs/
tests/
```

---

# PERSON 1 - Phase 1
# ROS2 Foundation Setup

## Tasks

### Install

```bash
sudo apt install ros-humble-desktop
```

### Create Workspace

```bash
mkdir -p ~/ugv_ws/src
cd ~/ugv_ws
colcon build
```

---

# PERSON 1 - Phase 2
# Create Navigation Nodes

## Required Nodes

```text
/navigation_node
/path_planner_node
/occupancy_mapping_node
/fusion_node
/mission_controller_node
```

---

# PERSON 1 - Phase 3
# Occupancy Grid Implementation

## Objective

Convert LiDAR and ultrasonic software inputs into:

```text
0 = free
1 = obstacle
2 = unknown
```

---

# PERSON 1 - Phase 4
# A* Path Planning

## Objective

Implement:

- multiple path generation
- shortest path selection
- dynamic route updates

## Required Features

### Path Cost Formula

```text
Path Cost = Distance + Threat Weight
```

## Threat Weights

```text
Harmless = 0
Harmful = 100
Unknown = 50
```

---

# PERSON 1 - Phase 5
# Navigation Execution & Robotics Control Handoff

## Objectives

- autonomous movement logic
- turning logic
- path following
- collision prevention
- goal completion
- motion-command publishing contract

---

# PERSON 1 - Phase 6
# Sensor Fusion

## Objective

Combine:

- LiDAR
- ultrasonic
- AI detection results

into a unified environment model.

---

# PERSON 1 - Phase 7
# Map Testing

## MAP 1
Single shortest path.

## MAP 2
Single shortest path + harmful object.

## MAP 3
Dual shortest path + threat-aware routing.

---

# PERSON 1 - Final Deliverables

## Must Deliver

- functional ROS2 autonomy software system
- A* planner
- occupancy mapping
- sensor fusion engine
- threat-aware path planning
- mission completion logic
- hardware-facing navigation interfaces

---

# PERSON 1 - Codex Execution Prompts

## Prompt 1

```text
PERSON1_TASK_01:
Setup ROS2 Humble workspace for UGV autonomy architecture with modular navigation nodes.
```

## Prompt 2

```text
PERSON1_TASK_02:
Implement occupancy grid mapping using LiDAR and ultrasonic sensor data in ROS2.
```

## Prompt 3

```text
PERSON1_TASK_03:
Implement A* shortest path planner with support for dynamic threat-aware path weighting.
```

## Prompt 4

```text
PERSON1_TASK_04:
Create autonomous navigation node capable of movement toward goal coordinates while avoiding mapped obstacles.
```

## Prompt 5

```text
PERSON1_TASK_05:
Integrate sensor fusion system combining LiDAR, ultrasonic, and AI detection outputs.
```

---

# 6. PERSON 2 - Complete Implementation Roadmap

# PERSON 2
# ROLE: AI & VISION ENGINEER

---

# PERSON 2 - Primary Objective

Build the complete AI perception stack.

This includes:

- object detection
- harmful/harmless classification
- real-time inference
- alert generation
- detection optimization
- camera ROS2/software pipeline

---

# PERSON 2 - Directory Ownership

```text
ai/
ros2_ws/src/vision/
ros2_ws/src/threat_detection/
models/
dataset/
configs/
tests/
```

---

# PERSON 2 - Phase 1
# AI Environment Setup

## Install

```bash
pip install ultralytics
pip install opencv-python
pip install torch torchvision
```

---

# PERSON 2 - Phase 2
# Dataset Collection

## Objective

Capture:

- harmful objects
- harmless objects

## Dataset Requirements

### Harmful Examples

- weapon-like objects
- simulated explosives
- military props
- threat markers

### Harmless Examples

- bottles
- boxes
- chairs
- civilian objects

---

# PERSON 2 - Phase 3
# Data Labeling

## Tool

Use:

- LabelImg

## Labels

```text
harmful
harmless
```

---

# PERSON 2 - Phase 4
# YOLOv8 Training

## Recommended Model

```text
YOLOv8n
```

## Training Command

```bash
yolo task=detect mode=train model=yolov8n.pt data=data.yaml epochs=100 imgsz=640
```

---

# PERSON 2 - Phase 5
# Model Optimization

## Convert to ONNX

```bash
yolo export model=best.pt format=onnx
```

---

# PERSON 2 - Phase 6
# Real-Time Inference Pipeline

## Objectives

- camera streaming
- real-time inference
- bounding box generation
- threat classification
- ROS2 publishing
- detection message contracts for navigation integration

---

# PERSON 2 - Phase 7
# Alert System

## Required Alerts

### If harmful object detected

```text
[ALERT] Harmful object detected.
Mission continuing.
```

---

# PERSON 2 - Phase 8
# Detection Optimization

## Goals

- increase FPS
- reduce latency
- lower CPU usage
- optimize inference

---

# PERSON 2 - Final Deliverables

## Must Deliver

- custom dataset
- trained YOLO model
- real-time inference system
- threat classification system
- alert system
- ROS2 AI detection node
- camera-to-AI software pipeline

---

# PERSON 2 - Codex Execution Prompts

## Prompt 1

```text
PERSON2_TASK_01:
Setup AI training environment for YOLOv8 harmful vs harmless object detection.
```

## Prompt 2

```text
PERSON2_TASK_02:
Create dataset structure and training pipeline for binary threat classification.
```

## Prompt 3

```text
PERSON2_TASK_03:
Implement real-time OpenCV camera pipeline integrated with YOLOv8 inference.
```

## Prompt 4

```text
PERSON2_TASK_04:
Build ROS2 vision node publishing harmful and harmless object detections.
```

## Prompt 5

```text
PERSON2_TASK_05:
Optimize YOLO inference pipeline for Raspberry Pi embedded deployment.
```

---

# 7. PERSON 3 - Complete Implementation Roadmap

# PERSON 3
# ROLE: HARDWARE ASSEMBLY & PLATFORM ENABLEMENT

---

# PERSON 3 - Primary Objective

Build and enable the physical UGV platform so the software team can connect
real code to real hardware.

This includes:

- wiring
- sensor mounting
- Raspberry Pi configuration
- motor mounting
- power systems
- hardware reliability
- chassis readiness

---

# PERSON 3 - Directory Ownership

```text
firmware/
hardware/
docs/
```

---

# PERSON 3 - Phase 1
# Raspberry Pi Setup

## Objectives

- install OS
- configure SSH
- configure I2C
- configure GPIO
- configure camera

## Enable Interfaces

```bash
sudo raspi-config
```

Enable:

- camera
- I2C
- SSH

---

# PERSON 3 - Phase 2
# Sensor and Motor Mounting

## Objectives

- mount motor driver hardware
- mount motors securely
- verify cable routing
- verify connector fit and board placement

---

# PERSON 3 - Phase 3
# Sensor Enablement

## Objectives

- mount LiDAR
- mount ultrasonic sensor
- mount camera
- verify electrical connectivity
- verify devices are physically recognized by the Pi

---

# PERSON 3 - Phase 4
# Raspberry Pi Platform Bring-Up

## Objectives

- OS installation
- SSH access
- interface enablement
- basic device checks

---

# PERSON 3 - Phase 5
# Power and Stability

## Objectives

- stable voltage
- power distribution
- thermal monitoring
- battery management

---

# PERSON 3 - Phase 6
# Physical Validation Support

## Objectives

- help validate hardware with the software team
- document pinouts and connections
- report hardware constraints
- support bench testing and troubleshooting

---

# PERSON 3 - Final Deliverables

## Must Deliver

- stable Raspberry Pi system
- functional sensors at the physical/electrical level
- functional motors at the physical/electrical level
- reliable physical platform
- stable power architecture
- assembly and wiring notes

---

# PERSON 3 - Codex Execution Prompts

## Prompt 1

```text
PERSON3_TASK_01:
Setup Raspberry Pi hardware environment for military-grade UGV system.
```

## Prompt 2

```text
PERSON3_TASK_02:
Assemble and wire the Waveshare Servo Driver HAT, motors, and power connections on the UGV platform.
```

## Prompt 3

```text
PERSON3_TASK_03:
Mount and enable LiDAR, ultrasonic, and camera hardware so the software team can consume them.
```

## Prompt 4

```text
PERSON3_TASK_04:
Validate motor and power wiring readiness for software-driven control testing.
```

## Prompt 5

```text
PERSON3_TASK_05:
Document the final hardware assembly, pin mapping, and bring-up checklist.
```

---

# 8. Integration Phase

# Critical Phase

Integration begins only after:

- Person 1 validates navigation software
- Person 2 validates AI detection software
- Person 3 validates hardware readiness

---

# 9. Final System Integration Order

## Step 1
Integrate hardware-ready devices with software drivers.

## Step 2
Integrate ROS2 communication.

## Step 3
Integrate navigation stack.

## Step 4
Integrate AI detection.

## Step 5
Integrate alert system.

## Step 6
Integrate threat-aware path planning.

## Step 7
Run simulation tests.

## Step 8
Run physical map tests.

---

# 10. Map Validation Execution

# MAP 1

Expected:

- shortest path chosen
- harmless object detected
- goal reached

---

# MAP 2

Expected:

- harmful object detected
- alert triggered
- goal reached

---

# MAP 3

Expected:

- safer shortest path selected
- harmful path avoided
- goal reached

---

# 11. Git Workflow Strategy

## Recommended Branches

```text
main
person1-navigation
person2-ai
person3-assembly
integration
```

---

# 12. Commit Rules

## Commit Format

```text
[PERSON1] Added A* planner
[PERSON2] Trained YOLOv8n model
[PERSON3] Completed hardware assembly checklist
```

---

# 13. Daily Workflow

## Morning

- pull latest changes
- sync dependencies
- review integration blockers

## During Work

- work only inside assigned directories
- push frequently

## End of Day

- commit changes
- update progress log
- document issues

---

# 14. Coding Standards

## Python Standards

- modular functions
- type hints
- ROS2 logging
- exception handling
- config-driven architecture

---

# 15. Testing Requirements

## Unit Testing

Each module must be independently testable.

## Integration Testing

Validate:

- ROS communication
- sensor updates
- AI detections
- navigation decisions

---

# 16. Critical Engineering Rules

## Never

- hardcode sensor values
- mix AI and navigation logic in one file
- directly manipulate hardware inside AI modules
- block navigation during inference

---

# 17. Final Target Architecture

The final UGV system should function as:

- autonomous navigation platform
- threat-aware decision system
- real-time AI perception engine
- physically stable robotics platform
- modular prototype ready for further research

---

# 18. Final Success Criteria

Project is successful if:

- UGV autonomously reaches target
- correctly identifies harmful/harmless objects
- avoids obstacles
- triggers alerts reliably
- selects safest shortest route
- operates continuously without crash
- maintains stable ROS2 communication
- performs real-time inference on embedded hardware

---

# 19. Final Engineering Advice

This project should be approached like a scalable autonomous systems platform.

The key to success is:

- modularity
- subsystem isolation
- clean interfaces
- incremental validation
- disciplined integration
