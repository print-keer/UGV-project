# UGV TEAM-BASED IMPLEMENTATION WORKFLOW

# Military Grade Autonomous UGV — Distributed Execution Blueprint

---

# 1. DOCUMENT PURPOSE

This document is designed for a 3-member engineering team building the UGV project collaboratively.

The architecture is intentionally divided so that:

- Each team member can independently clone the repository
- Each member can work in parallel
- Codex can execute tasks based on PERSON tags
- Integration conflicts are minimized
- Development becomes modular and scalable

This workflow follows professional robotics engineering methodology.

---

# 2. TEAM STRUCTURE

## PERSON 1 — AUTONOMY & NAVIGATION ENGINEER

Responsible for:
- ROS2 architecture
- Path planning
- Mapping
- Navigation stack
- Sensor fusion logic
- Occupancy grid
- A* implementation
- Threat-aware route selection

Primary Domain:
AUTONOMOUS MOVEMENT

---

## PERSON 2 — AI & VISION ENGINEER

Responsible for:
- Dataset creation
- Object detection
- YOLO training
- Threat classification
- Camera processing
- Inference optimization
- Alert logic
- Detection pipeline

Primary Domain:
AI PERCEPTION SYSTEM

---

## PERSON 3 — HARDWARE & EMBEDDED SYSTEMS ENGINEER

Responsible for:
- Raspberry Pi setup
- Servo driver integration
- Motor interfacing
- Sensor wiring
- LiDAR setup
- Ultrasonic integration
- Power systems
- GPIO/I2C communication
- Hardware debugging

Primary Domain:
PHYSICAL SYSTEMS

---

# 3. GLOBAL DEVELOPMENT STRATEGY

## IMPORTANT RULE

No member should directly modify another member's module unless integration phase begins.

Each subsystem must:

- Build independently
- Run independently
- Be testable independently

Final integration happens only after module validation.

---

# 4. MASTER REPOSITORY STRUCTURE

```text
UGV/
│
├── autonomy/
├── ai/
├── firmware/
├── hardware/
├── ros2_ws/
├── simulation/
├── configs/
├── logs/
├── tests/
└── docs/
```

---

# 5. PERSON 1 — COMPLETE IMPLEMENTATION ROADMAP

# PERSON 1
# ROLE: AUTONOMY & NAVIGATION ENGINEER

---

# PERSON 1 — PRIMARY OBJECTIVE

Build the complete autonomous navigation stack.

This includes:

- Mapping
- Navigation
- Path planning
- Route optimization
- Collision prevention
- Threat-aware routing

---

# PERSON 1 — DIRECTORY OWNERSHIP

```text
autonomy/
ros2_ws/src/navigation/
ros2_ws/src/path_planner/
ros2_ws/src/mapping/
simulation/
```

---

# PERSON 1 — PHASE 1
# ROS2 FOUNDATION SETUP

## Tasks

### Install:

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

# PERSON 1 — PHASE 2
# CREATE NAVIGATION NODES

## Required Nodes

```text
/navigation_node
/path_planner_node
/occupancy_mapping_node
/fusion_node
/mission_controller_node
```

---

# PERSON 1 — PHASE 3
# OCCUPANCY GRID IMPLEMENTATION

## Objective

Convert LiDAR data into:

```text
0 = free
1 = obstacle
2 = unknown
```

---

# PERSON 1 — PHASE 4
# A* PATH PLANNING

## Objective

Implement:

- Multiple path generation
- Shortest path selection
- Dynamic route updates

---

## Required Features

### Path Cost Formula

```text
Path Cost = Distance + Threat Weight
```

---

## Threat Weights

```text
Harmless = 0
Harmful = 100
Unknown = 50
```

---

# PERSON 1 — PHASE 5
# NAVIGATION EXECUTION

## Objectives

- Autonomous movement
- Turning logic
- Path following
- Collision prevention
- Goal completion

---

# PERSON 1 — PHASE 6
# SENSOR FUSION

## Objective

Combine:

- LiDAR
- Ultrasonic
- AI detection results

into a unified environment model.

---

# PERSON 1 — PHASE 7
# MAP TESTING

## MAP 1
Single shortest path.

## MAP 2
Single shortest path + harmful object.

## MAP 3
Dual shortest path + threat-aware routing.

---

# PERSON 1 — FINAL DELIVERABLES

## Must Deliver

- Functional ROS2 navigation system
- A* planner
- Occupancy mapping
- Sensor fusion engine
- Threat-aware path planning
- Mission completion logic

---

# PERSON 1 — CODEX EXECUTION PROMPTS

## Prompt 1

```text
PERSON1_TASK_01:
Setup ROS2 Humble workspace for UGV autonomy architecture with modular navigation nodes.
```

---

## Prompt 2

```text
PERSON1_TASK_02:
Implement occupancy grid mapping using LiDAR sensor data in ROS2.
```

---

## Prompt 3

```text
PERSON1_TASK_03:
Implement A* shortest path planner with support for dynamic threat-aware path weighting.
```

---

## Prompt 4

```text
PERSON1_TASK_04:
Create autonomous navigation node capable of movement toward goal coordinates while avoiding mapped obstacles.
```

---

## Prompt 5

```text
PERSON1_TASK_05:
Integrate sensor fusion system combining LiDAR, ultrasonic, and AI detection outputs.
```

---

# 6. PERSON 2 — COMPLETE IMPLEMENTATION ROADMAP

# PERSON 2
# ROLE: AI & VISION ENGINEER

---

# PERSON 2 — PRIMARY OBJECTIVE

Build the complete AI perception stack.

This includes:

- Object detection
- Harmful/harmless classification
- Real-time inference
- Alert generation
- Detection optimization

---

# PERSON 2 — DIRECTORY OWNERSHIP

```text
ai/
ros2_ws/src/vision/
ros2_ws/src/threat_detection/
models/
dataset/
```

---

# PERSON 2 — PHASE 1
# AI ENVIRONMENT SETUP

## Install:

```bash
pip install ultralytics
pip install opencv-python
pip install torch torchvision
```

---

# PERSON 2 — PHASE 2
# DATASET COLLECTION

## Objective

Capture:

- Harmful objects
- Harmless objects

---

## Dataset Requirements

### Harmful Examples

- Weapon-like objects
- Simulated explosives
- Military props
- Threat markers

### Harmless Examples

- Bottles
- Boxes
- Chairs
- Civilian objects

---

# PERSON 2 — PHASE 3
# DATA LABELING

## Tool

Use:

- LabelImg

---

## Labels

```text
harmful
harmless
```

---

# PERSON 2 — PHASE 4
# YOLOv8 TRAINING

## Recommended Model

```text
YOLOv8n
```

---

## Training Command

```bash
yolo task=detect mode=train model=yolov8n.pt data=data.yaml epochs=100 imgsz=640
```

---

# PERSON 2 — PHASE 5
# MODEL OPTIMIZATION

## Convert to ONNX

```bash
yolo export model=best.pt format=onnx
```

---

# PERSON 2 — PHASE 6
# REAL-TIME INFERENCE PIPELINE

## Objectives

- Camera streaming
- Real-time inference
- Bounding box generation
- Threat classification
- ROS2 publishing

---

# PERSON 2 — PHASE 7
# ALERT SYSTEM

## Required Alerts

### If harmful object detected:

```text
[ALERT] Harmful object detected.
Mission continuing.
```

---

# PERSON 2 — PHASE 8
# DETECTION OPTIMIZATION

## Goals

- Increase FPS
- Reduce latency
- Lower CPU usage
- Optimize inference

---

# PERSON 2 — FINAL DELIVERABLES

## Must Deliver

- Custom dataset
- Trained YOLO model
- Real-time inference system
- Threat classification system
- Alert system
- ROS2 AI detection node

---

# PERSON 2 — CODEX EXECUTION PROMPTS

## Prompt 1

```text
PERSON2_TASK_01:
Setup AI training environment for YOLOv8 harmful vs harmless object detection.
```

---

## Prompt 2

```text
PERSON2_TASK_02:
Create dataset structure and training pipeline for binary threat classification.
```

---

## Prompt 3

```text
PERSON2_TASK_03:
Implement real-time OpenCV camera pipeline integrated with YOLOv8 inference.
```

---

## Prompt 4

```text
PERSON2_TASK_04:
Build ROS2 vision node publishing harmful and harmless object detections.
```

---

## Prompt 5

```text
PERSON2_TASK_05:
Optimize YOLO inference pipeline for Raspberry Pi embedded deployment.
```

---

# 7. PERSON 3 — COMPLETE IMPLEMENTATION ROADMAP

# PERSON 3
# ROLE: HARDWARE & EMBEDDED SYSTEMS ENGINEER

---

# PERSON 3 — PRIMARY OBJECTIVE

Build the complete physical UGV platform.

This includes:

- Wiring
- Sensor integration
- Raspberry Pi configuration
- Motor control
- Power systems
- Hardware reliability

---

# PERSON 3 — DIRECTORY OWNERSHIP

```text
firmware/
hardware/
ros2_ws/src/hardware_interface/
```

---

# PERSON 3 — PHASE 1
# RASPBERRY PI SETUP

## Objectives

- Install OS
- Configure SSH
- Configure I2C
- Configure GPIO
- Configure camera

---

## Enable Interfaces

```bash
sudo raspi-config
```

Enable:

- Camera
- I2C
- SSH

---

# PERSON 3 — PHASE 2
# SERVO DRIVER INTEGRATION

## Hardware

- Waveshare Servo Driver HAT (B)

---

## Objectives

- PWM testing
- Servo testing
- Motor testing
- Direction control

---

# PERSON 3 — PHASE 3
# LiDAR INTEGRATION

## Objectives

- LiDAR communication
- Distance reading
- ROS2 topic publishing
- Sensor calibration

---

# PERSON 3 — PHASE 4
# ULTRASONIC SENSOR INTEGRATION

## Objectives

- Near obstacle detection
- Emergency stop trigger
- ROS2 communication

---

# PERSON 3 — PHASE 5
# CAMERA INTEGRATION

## Objectives

- 1080p stream validation
- Day/night mode validation
- OpenCV camera access

---

# PERSON 3 — PHASE 6
# MOTOR CONTROL SYSTEM

## Objectives

- Forward movement
- Reverse movement
- Turning
- Speed control
- Emergency stop

---

# PERSON 3 — PHASE 7
# POWER SYSTEM STABILIZATION

## Objectives

- Stable voltage
- Power distribution
- Thermal monitoring
- Battery management

---

# PERSON 3 — FINAL DELIVERABLES

## Must Deliver

- Stable Raspberry Pi system
- Functional sensors
- Functional motors
- ROS2 hardware interfaces
- Reliable physical platform
- Stable power architecture

---

# PERSON 3 — CODEX EXECUTION PROMPTS

## Prompt 1

```text
PERSON3_TASK_01:
Setup Raspberry Pi hardware environment for military-grade UGV system.
```

---

## Prompt 2

```text
PERSON3_TASK_02:
Integrate Waveshare Servo Driver HAT with Raspberry Pi using I2C communication.
```

---

## Prompt 3

```text
PERSON3_TASK_03:
Implement LiDAR and ultrasonic sensor ROS2 hardware interface nodes.
```

---

## Prompt 4

```text
PERSON3_TASK_04:
Create motor control firmware supporting forward, reverse, turning, and emergency stop.
```

---

## Prompt 5

```text
PERSON3_TASK_05:
Integrate Raspberry Pi camera system with OpenCV validation pipeline.
```

---

# 8. INTEGRATION PHASE

# CRITICAL PHASE

Integration begins ONLY after:

- Person 1 validates navigation
- Person 2 validates AI detection
- Person 3 validates hardware systems

---

# 9. FINAL SYSTEM INTEGRATION ORDER

## Step 1
Integrate hardware drivers.

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

# 10. MAP VALIDATION EXECUTION

# MAP 1

Expected:

- Shortest path chosen
- Harmless object detected
- Goal reached

---

# MAP 2

Expected:

- Harmful object detected
- Alert triggered
- Goal reached

---

# MAP 3

Expected:

- Safer shortest path selected
- Harmful path avoided
- Goal reached

---

# 11. GIT WORKFLOW STRATEGY

## Recommended Branches

```text
main
person1-navigation
person2-ai
person3-hardware
integration
```

---

# 12. COMMIT RULES

## Commit Format

```text
[PERSON1] Added A* planner
[PERSON2] Trained YOLOv8n model
[PERSON3] Integrated LiDAR driver
```

---

# 13. DAILY WORKFLOW

## Morning

- Pull latest changes
- Sync dependencies
- Review integration blockers

## During Work

- Work only inside assigned directories
- Push frequently

## End of Day

- Commit changes
- Update progress log
- Document issues

---

# 14. CODING STANDARDS

## Python Standards

- Modular functions
- Type hints
- ROS2 logging
- Exception handling
- Config-driven architecture

---

# 15. TESTING REQUIREMENTS

## Unit Testing

Each module must be independently testable.

---

## Integration Testing

Validate:

- ROS communication
- Sensor updates
- AI detections
- Navigation decisions

---

# 16. CRITICAL ENGINEERING RULES

## NEVER:

- Hardcode sensor values
- Mix AI and navigation logic in one file
- Directly manipulate hardware inside AI modules
- Block navigation during inference

---

# 17. FINAL TARGET ARCHITECTURE

The final UGV system should function as:

- Autonomous navigation platform
- Threat-aware decision system
- Real-time AI perception engine
- Embedded robotics platform
- Modular military-grade prototype

---

# 18. FINAL SUCCESS CRITERIA

Project is successful if:

- UGV autonomously reaches target
- Correctly identifies harmful/harmless objects
- Avoids obstacles
- Triggers alerts reliably
- Selects safest shortest route
- Operates continuously without crash
- Maintains stable ROS2 communication
- Performs real-time inference on embedded hardware

---

# 19. FINAL ENGINEERING ADVICE

This project should not be approached like:

A normal robotics college project.

It should be approached like:

A scalable autonomous systems engineering platform.

The key to success is:

- modularity
- subsystem isolation
- clean interfaces
- incremental validation
- disciplined integration

If implemented correctly, this architecture can evolve into:

- tactical reconnaissance UGV
- autonomous patrol platform
- intelligent surveillance robot
- defense research platform
- swarm robotics system
- AI-assisted autonomous military vehicle

