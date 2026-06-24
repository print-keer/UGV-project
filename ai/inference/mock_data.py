from __future__ import annotations

from dataclasses import dataclass

from ai.threat_classifier.types import BoundingBox, Detection


@dataclass(frozen=True)
class MockFrame:
    frame_id: str
    description: str
    detections: tuple[Detection, ...]


def load_mock_frames() -> list[MockFrame]:
    return [
        MockFrame(
            frame_id="frame-clear-001",
            description="Indoor corridor with harmless storage boxes.",
            detections=(
                Detection(
                    label="harmless",
                    confidence=0.94,
                    bounding_box=BoundingBox(32, 48, 144, 224),
                    source="mock_dataset",
                ),
            ),
        ),
        MockFrame(
            frame_id="frame-threat-001",
            description="Outdoor checkpoint scene with simulated threat marker.",
            detections=(
                Detection(
                    label="harmful",
                    confidence=0.91,
                    bounding_box=BoundingBox(96, 60, 220, 260),
                    source="mock_dataset",
                ),
                Detection(
                    label="harmless",
                    confidence=0.82,
                    bounding_box=BoundingBox(12, 120, 74, 246),
                    source="mock_dataset",
                ),
            ),
        ),
        MockFrame(
            frame_id="frame-unknown-001",
            description="Low-light scene with partially occluded object.",
            detections=(
                Detection(
                    label="unknown_object",
                    confidence=0.51,
                    bounding_box=BoundingBox(40, 84, 166, 238),
                    source="mock_dataset",
                ),
            ),
        ),
    ]
