# UGV PROJECT — MILITARY GRADE AUTONOMOUS GROUND VEHICLE

## Project Classification

High-Efficiency Autonomous Military Surveillance and Threat-Aware Navigation UGV

---

# 1. PROJECT OVERVIEW

## Objective

The objective of this project is to design and develop a fully functional autonomous Unmanned Ground Vehicle (UGV) capable of:

1. Autonomous navigation
2. Real-time shortest-path computation
3. Obstacle and terrain awareness
4. Harmful vs harmless object classification
5. Autonomous alert triggering
6. Simultaneous navigation and object detection
7. Goal-based mission completion
8. Efficient decision-making under constrained embedded hardware

The final system must operate as a semi-realistic military-grade prototype emphasizing:

- Real-time autonomy
- Modular AI architecture
- Efficient embedded inference
- Scalable autonomy stack
- Sensor fusion
- Reliable path planning
- Mission continuity under threat detection

---

# 2. CORE FUNCTIONAL REQUIREMENTS

## Functional Goals

### Navigation System
The UGV must:

- Scan environment continuously
- Identify valid paths
- Compute shortest route
- Avoid collisions
- Continue movement autonomously
- Reach destination without human intervention

### Object Detection System
The UGV must:

- Detect objects during navigation
- Classify detected object
- Determine whether object is:
  - Harmful
  - Harmless

### Alert System
If harmful object is detected:

- Trigger warning alert
- Log detection event
- Continue mission
- Reach final target

### Multi-Objective Intelligence
The system must:

- Navigate and classify simultaneously
- Maintain low latency
- Operate in real time
- Avoid blocking navigation pipeline during detection

---

# 3. AVAILABLE HARDWARE COMPONENTS

## Current Hardware Inventory

### Compute Unit
- Raspberry Pi 4

### Motor Driver
- Waveshare Servo Driver HAT (B)
- 16-Channel
- 12-bit PWM
- I2C communication

### Sensors
#### LiDAR Distance Sensor
Used for:
- Mapping
- Distance estimation
- Path planning
- Obstacle awareness
- Environment scanning

#### Grove Ultrasonic Ranger
Used for:
- Close-range obstacle detection
- Emergency collision prevention
- Backup sensing layer

### Vision System
#### 1080p IR-Cut Camera
Features:
- Day/night mode
- Automatic IR switching
- Raspberry Pi compatible

Used for:
- Object detection
- Threat classification
- Image streaming
- Data collection

---

# 4. HIGH LEVEL SYSTEM ARCHITECTURE

```text
                    +----------------------+
                    |   Mission Goal Node  |
                    +----------+-----------+
                               |
                               v
+-----------------------------------------------------------+
|                   AUTONOMY CORE                           |
|-----------------------------------------------------------|
|                                                           |
|  +----------------+    +------------------------------+   |
|  | Path Planner   |<-->| Environment Mapping System   |   |
|  +----------------+    +------------------------------+   |
|                                                           |
|  +----------------+    +------------------------------+   |
|  | Object Detect  |<-->| Threat Classification System |   |
|  +----------------+    +------------------------------+   |
|                                                           |
|  +----------------+    +------------------------------+   |
|  | Motion Control |<-->| Sensor Fusion Engine         |   |
|  +----------------+    +------------------------------+   |
|                                                           |
+-----------------------------------------------------------+
                               |
                               v
                    +----------------------+
                    |  Motor Driver Layer  |
                    +----------------------+
```

---

# 5. PROPOSED SOFTWARE STACK

## Operating System
### Recommended
- Ubuntu Server 22.04 (Raspberry Pi)

Alternative:
- Raspberry Pi OS 64-bit

Recommended because:
- Better ROS2 compatibility
- Better package management
- Better robotics ecosystem support

---

# 6. CORE SOFTWARE FRAMEWORK

## Primary Robotics Framework
# ROS2 (Robot Operating System 2)

### Why ROS2?

ROS2 is mandatory for a professional robotics architecture because it provides:

- Modular robotics nodes
- Real-time communication
- Sensor abstraction
- Distributed computation
- Scalable architecture
- Industry-standard robotics middleware
- Simulation support
- Hardware abstraction

### Recommended Version
- ROS2 Humble

---

# 7. AUTONOMY PIPELINE

## Full Mission Workflow

```text
START
  |
  v
Initialize Sensors
  |
  v
Generate Environment Map
  |
  v
Compute Possible Paths
  |
  v
Select Shortest Path
  |
  v
Begin Navigation
  |
  v
Continuously Scan Environment
  |
  +--------------------------+
  |                          |
  v                          v
Obstacle Check          Camera Detection
  |                          |
  v                          v
Collision Avoidance     Threat Classification
                             |
             +---------------+---------------+
             |                               |
             v                               v
      Harmless Object                Harmful Object
             |                               |
             v                               v
      Continue Mission            Trigger Alert
                                             |
                                             v
                                    Continue Mission
                                             |
                                             v
                                      Reach Goal
                                             |
                                             v
                                           END
```

---

# 8. NAVIGATION SYSTEM DESIGN

## Core Requirement
UGV must identify shortest path among multiple possible paths.

---

# 9. BEST ALGORITHMS FOR PATH PLANNING

## Recommended Architecture

### Global Planner
# A* (A-Star) Algorithm

### Why A*?

A* is ideal because:

- Efficient
- Deterministic
- Fast on embedded systems
- Optimal path finding
- Easy to debug
- Works well with occupancy grids
- Lightweight for Raspberry Pi

### Do NOT use initially
Avoid:
- Deep Reinforcement Learning navigation
- Complex SLAM-based AI planners
- Transformer-based planners

Reason:
- Excessive compute requirements
- Unnecessary complexity for prototype
- Difficult debugging
- High latency on Raspberry Pi

---

# 10. ENVIRONMENT REPRESENTATION

## Occupancy Grid Mapping

Environment is represented as:

```text
0 = free cell
1 = obstacle
2 = unknown
```

LiDAR + Ultrasonic data will continuously update occupancy map.

---

# 11. SENSOR FUSION STRATEGY

## Sensor Responsibilities

### LiDAR
Primary:
- Long-range mapping
- Path generation
- Obstacle mapping

### Ultrasonic Sensor
Primary:
- Near-field emergency stop
- Blind spot detection
- Collision backup layer

### Camera
Primary:
- Object recognition
- Threat classification

---

# 12. OBJECT DETECTION SYSTEM

## Core Requirement
System must classify:

- Harmful object
- Harmless object

in real time while navigation continues.

---

# 13. BEST MODEL FOR EMBEDDED DETECTION

# Recommended Model
## YOLOv8n

### Why YOLOv8n?

- Extremely lightweight
- Excellent Raspberry Pi compatibility
- Fast inference
- Real-time capable
- Easy training pipeline
- Good community support
- Military-grade prototype feasible

---

# 14. OBJECT CLASSIFICATION STRATEGY

## Initial Simplification Strategy

Instead of detecting thousands of classes:

Use binary threat classification.

### Classes

#### Harmful
Examples:
- Weapon-like object
- Military threat object
- Dangerous obstacle
- Simulated explosive marker

#### Harmless
Examples:
- Civilian object
- Box
- Bottle
- Chair
- Safe object

---

# 15. DATASET CREATION STRATEGY

## CRITICAL DECISION
Do NOT attempt huge dataset training initially.

Instead:

Build controlled custom dataset.

---

# 16. DATA COLLECTION PIPELINE

## Step 1 — Capture Images

Capture images from:

- Different lighting
- Different angles
- Different distances
- Day/night mode
- Partial occlusions

Target:
- 500–1000 images initially

---

## Step 2 — Label Dataset

Recommended Tool:
- LabelImg

Labels:

```text
harmful
harmless
```

---

## Step 3 — Train YOLOv8

Recommended Environment:

Train on:
- Laptop with GPU
OR
- Google Colab

Never train directly on Raspberry Pi.

Pi should only:
- Run inference
- Execute autonomy stack

---

# 17. TRAINING PIPELINE

## Recommended Framework

- Ultralytics YOLOv8

### Installation

```bash
pip install ultralytics
```

---

## Training Command

```bash
yolo task=detect mode=train model=yolov8n.pt data=data.yaml epochs=100 imgsz=640
```

---

# 18. MODEL OPTIMIZATION

## Convert Model

Convert trained model into:

- ONNX
- TensorRT (future optimization)

Recommended for Raspberry Pi:

```bash
yolo export model=best.pt format=onnx
```

---

# 19. REAL-TIME INFERENCE PIPELINE

```text
Camera Feed
    |
    v
Frame Capture
    |
    v
YOLOv8 Inference
    |
    v
Threat Classification
    |
    +---------------------+
    |                     |
    v                     v
Harmless             Harmful
    |                     |
    |               Trigger Alert
    |                     |
    +----------+----------+
               |
               v
       Continue Navigation
```

---

# 20. ALERT SYSTEM DESIGN

## Required Alerts

### Software Alerts
- Console warning
- ROS topic message
- Mission log entry

### Hardware Alerts (Future)
- Buzzer
- LED
- Radio transmission

---

# 21. CONCURRENCY REQUIREMENT

## VERY IMPORTANT
Navigation and object detection must run simultaneously.

---

# 22. HOW TO IMPLEMENT CONCURRENCY

## ROS2 Node Architecture

### Recommended Nodes

```text
/vision_node
/navigation_node
/path_planner_node
/motor_control_node
/lidar_node
/ultrasonic_node
/alert_node
/fusion_node
```

Each node runs independently.

This is why ROS2 is essential.

---

# 23. RECOMMENDED PROJECT REPOSITORY STRUCTURE

```text
UGV/
│
├── firmware/
│   ├── motor_controller/
│   ├── sensor_interface/
│   └── pwm_driver/
│
├── autonomy/
│   ├── path_planning/
│   ├── obstacle_avoidance/
│   ├── occupancy_mapping/
│   └── mission_controller/
│
├── ai/
│   ├── dataset/
│   ├── training/
│   ├── inference/
│   ├── models/
│   └── threat_classifier/
│
├── ros2_ws/
│   ├── src/
│   └── install/
│
├── simulation/
│   ├── gazebo/
│   └── maps/
│
├── configs/
│
├── logs/
│
├── tests/
│
├── docs/
│
└── deployment/
```

---

# 24. MAP TESTING STRATEGY

# MAP 1

## Objective
Single shortest path.

### Expected Behavior

- UGV identifies shortest path
- Detects harmless object
- Continues mission
- Reaches goal

---

# MAP 2

## Objective
Single shortest path.

### Expected Behavior

- UGV identifies shortest path
- Detects harmful object
- Triggers alert
- Continues mission
- Reaches goal

---

# MAP 3

## Objective
Two shortest paths.

### Expected Behavior

- UGV evaluates both routes
- Detects harmful object in one route
- Detects harmless object in other route
- Chooses safer optimal path
- Reaches goal

---

# 25. IMPORTANT ARCHITECTURE IMPROVEMENT

## CRITICAL DESIGN INSIGHT

Your current logic says:

Even if harmful object detected → continue on same path.

For a military-grade system this is incomplete.

Better logic:

### Threat-Aware Path Planning

Each path gets:

```text
Total Cost = Distance Cost + Threat Cost
```

Example:

```text
Path A:
Distance = 5
Threat = Harmful
Total Cost = 5 + 100

Path B:
Distance = 6
Threat = Harmless
Total Cost = 6 + 0
```

Result:
- Choose Path B.

This makes system significantly more intelligent.

---

# 26. FINAL RECOMMENDED DECISION ENGINE

## Hybrid Path Decision

### Formula

Distance-based navigation alone is weak.

Use:

```text
Final Score = Path Distance + Threat Weight + Risk Weight
```

---

# 27. RECOMMENDED EXECUTION PHASES

# PHASE 1 — HARDWARE INTEGRATION

## Goals

- Motor movement
- Sensor communication
- Camera stream
- LiDAR reading
- PWM control

### Deliverables

- Motor driver working
- Camera feed active
- Sensor data accessible
- ROS2 topics publishing

---

# PHASE 2 — BASIC AUTONOMOUS MOVEMENT

## Goals

- Straight movement
- Turning
- Obstacle avoidance
- Occupancy map generation

### Deliverables

- Autonomous movement
- Collision prevention

---

# PHASE 3 — PATH PLANNING

## Goals

- Implement A*
- Multiple path evaluation
- Shortest path computation

### Deliverables

- Successful shortest-path navigation

---

# PHASE 4 — OBJECT DETECTION

## Goals

- Dataset creation
- YOLO training
- Real-time inference

### Deliverables

- Harmful/harmless classification

---

# PHASE 5 — AUTONOMY FUSION

## Goals

- Merge navigation + detection
- Simultaneous execution
- Threat-aware planning

### Deliverables

- Fully autonomous mission execution

---

# PHASE 6 — ADVANCED OPTIMIZATION

## Goals

- FPS optimization
- Latency reduction
- Efficient threading
- Memory optimization

---

# 28. CRITICAL PERFORMANCE TARGETS

## Navigation

- Planning latency < 100ms

## Detection

- Inference speed 10–20 FPS minimum

## Sensor Update Rate

- 20Hz minimum

## Obstacle Response

- < 200ms reaction

---

# 29. SIMULATION REQUIREMENT

## STRONGLY RECOMMENDED

Before physical testing:

Use:
- Gazebo
- RViz

Reason:

- Prevent hardware damage
- Faster debugging
- Faster iteration
- Safer autonomy development

---

# 30. DEVELOPMENT STRATEGY

## Recommended Development Order

### Step 1
Hardware drivers

### Step 2
ROS2 communication

### Step 3
Manual movement

### Step 4
Sensor streaming

### Step 5
Occupancy mapping

### Step 6
A* path planning

### Step 7
Autonomous navigation

### Step 8
Dataset collection

### Step 9
YOLO training

### Step 10
Real-time detection

### Step 11
Fusion of AI + navigation

### Step 12
Threat-aware path selection

### Step 13
Simulation validation

### Step 14
Physical testing

### Step 15
Performance optimization

---

# 31. ADVANCED FUTURE IMPROVEMENTS

## Future Upgrade Roadmap

### SLAM Integration
Recommended:
- Cartographer
- RTAB-Map

### Advanced Threat Classification
Upgrade:
- Multi-class military detection

### Multi-Sensor Fusion
Add:
- IMU
- GPS
- Thermal camera

### Advanced AI
Future:
- Reinforcement Learning
- Behavior prediction
- Dynamic route adaptation

### Multi-Agent Swarm UGV
Future:
- Cooperative navigation
- Shared mapping
- Distributed threat intelligence

---

# 32. RECOMMENDED PROGRAMMING LANGUAGES

## Python
Use for:
- AI
- ROS2 nodes
- Rapid prototyping

## C++
Use later for:
- High-performance ROS2 nodes
- Real-time planning
- Motor control optimization

---

# 33. SECURITY CONSIDERATIONS

## Important for Military Architecture

### Protect:
- Sensor streams
- Mission logs
- AI models
- ROS communication

### Future Security Layers
- DDS security
- Encrypted communication
- Secure boot
- Signed firmware

---

# 34. LOGGING SYSTEM

## Every mission should log:

- Path selected
- Obstacles detected
- Threat detections
- Timestamp
- Sensor data
- Alerts triggered
- Mission completion status

---

# 35. FAILURE MODES

## System must handle:

### Camera failure
Fallback:
- Continue navigation only

### LiDAR failure
Fallback:
- Ultrasonic emergency mode

### Detection failure
Fallback:
- Unknown object classification

### Path blocked
Fallback:
- Recompute route

---

# 36. RECOMMENDED TEAM DIVISION

## AI Team
Responsible for:
- Dataset
- Training
- Detection

## Robotics Team
Responsible for:
- Sensors
- ROS2
- Navigation

## Systems Team
Responsible for:
- Integration
- Optimization
- Deployment

---

# 37. FINAL RECOMMENDED TECH STACK

## Robotics
- ROS2 Humble
- RViz
- Gazebo

## AI
- YOLOv8n
- PyTorch
- ONNX Runtime

## Embedded
- Raspberry Pi 4
- Python
- OpenCV

## Algorithms
- A*
- Occupancy Grid Mapping
- Sensor Fusion

---

# 38. MOST IMPORTANT ENGINEERING ADVICE

## DO NOT attempt everything simultaneously.

The biggest failure in robotics projects is:

Trying to build full autonomy before validating modules independently.

Correct strategy:

### Build incrementally.

Validate each subsystem separately.

Then integrate.

---

# 39. IDEAL INITIAL SUCCESS CRITERIA

## Minimum Viable Military Prototype

System is considered successful if:

- UGV autonomously reaches target
- Detects objects correctly
- Differentiates harmful vs harmless
- Triggers alerts reliably
- Avoids obstacles
- Chooses shortest/safest route
- Operates continuously without crash

---

# 40. FINAL CONCLUSION

This project should be treated as:

A modular autonomous robotics platform rather than a simple robot car.

The correct architecture is:

- ROS2-centered
- Modular node-based design
- AI-assisted navigation
- Threat-aware path planning
- Real-time sensor fusion
- Embedded optimized inference

The recommended approach is:

1. Hardware stabilization
2. Navigation foundation
3. AI perception
4. Multi-threaded autonomy
5. Threat-aware intelligence
6. Optimization
7. Simulation validation
8. Real-world deployment

If implemented correctly, this architecture can evolve into:

- Military reconnaissance UGV
- Autonomous patrol robot
- Surveillance platform
- Search-and-rescue robot
- Smart tactical ground system
- Multi-agent autonomous fleet

