from __future__ import annotations

import json
from typing import Any

from ai.inference.pipeline import FrameInferenceResult
from ai.threat_classifier.classifier import assess_detections
from ai.threat_classifier.types import BoundingBox, Detection, ThreatAssessment


def serialize_detection_result(result: FrameInferenceResult) -> str:
    payload = {
        "frame_id": result.frame_id,
        "description": result.description,
        "backend_name": result.backend_name,
        "detections": [
            {
                "label": detection.label,
                "confidence": detection.confidence,
                "bounding_box": {
                    "x_min": detection.bounding_box.x_min,
                    "y_min": detection.bounding_box.y_min,
                    "x_max": detection.bounding_box.x_max,
                    "y_max": detection.bounding_box.y_max,
                },
                "source": detection.source,
            }
            for detection in result.detections
        ],
    }
    return json.dumps(payload)


def deserialize_detection_result(payload: str) -> FrameInferenceResult:
    data = json.loads(payload)
    detections = tuple(_parse_detection(item) for item in data["detections"])
    return FrameInferenceResult(
        frame_id=data["frame_id"],
        description=data.get("description", ""),
        detections=detections,
        backend_name=data["backend_name"],
    )


def serialize_assessment(frame_id: str, assessment: ThreatAssessment) -> str:
    return json.dumps(
        {
            "frame_id": frame_id,
            "highest_priority_label": assessment.highest_priority_label,
            "harmful_count": assessment.harmful_count,
            "harmless_count": assessment.harmless_count,
            "unknown_count": assessment.unknown_count,
            "alert_required": assessment.alert_required,
            "summary": assessment.summary,
        }
    )


def deserialize_assessment(payload: str) -> dict[str, Any]:
    return json.loads(payload)


def build_assessment_payload(result: FrameInferenceResult) -> str:
    return serialize_assessment(result.frame_id, assess_detections(result.detections))


def _parse_detection(data: dict[str, Any]) -> Detection:
    box = data["bounding_box"]
    return Detection(
        label=data["label"],
        confidence=float(data["confidence"]),
        bounding_box=BoundingBox(
            x_min=int(box["x_min"]),
            y_min=int(box["y_min"]),
            x_max=int(box["x_max"]),
            y_max=int(box["y_max"]),
        ),
        source=data["source"],
    )
