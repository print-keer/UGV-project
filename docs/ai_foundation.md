# AI Foundation

This document describes the first Person 2 implementation milestone for the
UGV project.

## Scope

This milestone establishes the perception-side foundation without depending on
ROS2, camera hardware, or a trained YOLO model.

Implemented now:

- binary threat-classification data template under `ai/dataset/`
- pure Python inference abstraction under `ai/inference/`
- optional runtime image and camera loading through OpenCV
- optional runtime YOLO backend through Ultralytics
- pure Python threat-classification logic under `ai/threat_classifier/`
- JSON message contracts for detections and assessments
- ROS2 package scaffolding for `vision` and `threat_detection`
- mock perception flow that can be exercised in tests
- MVRSD dataset extraction and binary-dataset preparation support

Not included yet:

- custom ROS2 message types
- model export or Raspberry Pi optimization

## Intended package split

- `ai/inference/`: frame inference backends and frame-level detection outputs
- `ai/threat_classifier/`: harmful versus harmless assessment logic
- `ai/training/`: training configuration and launch helpers
- `ros2_ws/src/vision/`: ROS2 wrapper for camera and detection ingestion
- `ros2_ws/src/threat_detection/`: ROS2 wrapper for alerting and threat evaluation

## Local usage

Mock run:

```bash
python -m ai.inference.cli --mode mock
```

Image run with a trained model:

```bash
python -m ai.inference.cli --mode image --image-path path/to/frame.jpg --model-path ai/models/best.pt
```

Prepare the extracted MVRSD dataset for the current binary `harmful` setup:

```bash
python -m ai.dataset.prepare_mvrsd
```

Print the YOLO training command for the binary MVRSD setup:

```bash
python -m ai.training.train --preset mvrsd-binary --print-command-only
```

Print the YOLO training command for the original five-class MVRSD setup:

```bash
python -m ai.training.train --preset mvrsd-multiclass --print-command-only
```

## Current ROS2 topic contract

- `vision/detections`: `std_msgs/String` JSON payload with frame metadata and detections
- `threat_detection/alerts`: `std_msgs/String` JSON payload with frame assessment and alert summary

## Next implementation steps

1. Replace JSON-over-String topics with custom ROS2 message definitions.
2. Train a first YOLO model from the prepared MVRSD dataset.
3. Connect threat output into the navigation team’s future threat-cost logic.
4. Add live multi-frame camera streaming and throttling controls.
5. Add Raspberry Pi focused optimization and deployment notes.
