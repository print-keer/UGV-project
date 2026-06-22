from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

from ai.inference.backends import MockVisionBackend, RuntimeFrame, YoloVisionBackend
from ai.inference.mock_data import MockFrame, load_mock_frames
from ai.threat_classifier.types import Detection


@dataclass(frozen=True)
class FrameInferenceResult:
    frame_id: str
    description: str
    detections: tuple[Detection, ...]
    backend_name: str


class InferenceBackend(Protocol):
    name: str

    def infer(self, frame: MockFrame) -> Sequence[Detection]:
        """Return detections for a single frame."""


def run_mock_inference(
    frames: Sequence[MockFrame] | None = None,
    backend: InferenceBackend | None = None,
) -> list[FrameInferenceResult]:
    active_frames = list(frames) if frames is not None else load_mock_frames()
    active_backend = backend or MockVisionBackend()
    return [
        FrameInferenceResult(
            frame_id=frame.frame_id,
            description=frame.description,
            detections=tuple(active_backend.infer(frame)),
            backend_name=active_backend.name,
        )
        for frame in active_frames
    ]


def run_runtime_inference(
    frames: Sequence[RuntimeFrame],
    *,
    model_path: str,
    confidence_threshold: float = 0.25,
) -> list[FrameInferenceResult]:
    backend = YoloVisionBackend(
        model_path=model_path,
        confidence_threshold=confidence_threshold,
    )
    return [
        FrameInferenceResult(
            frame_id=frame.frame_id,
            description=frame.description,
            detections=tuple(backend.infer(frame)),
            backend_name=backend.name,
        )
        for frame in frames
    ]
