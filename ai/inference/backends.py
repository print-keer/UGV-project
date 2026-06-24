from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from ai.threat_classifier.types import BoundingBox, Detection


class InferenceDependencyError(RuntimeError):
    """Raised when a runtime inference dependency is unavailable."""


@dataclass(frozen=True)
class RuntimeFrame:
    frame_id: str
    image: Any
    description: str = ""


class MockVisionBackend:
    """Stand-in backend used before a trained model is available."""

    name = "mock-yolov8n"

    def infer(self, frame: Any) -> Sequence[Detection]:
        detections = getattr(frame, "detections", ())
        return tuple(
            Detection(
                label=detection.label,
                confidence=detection.confidence,
                bounding_box=detection.bounding_box,
                source=self.name,
            )
            for detection in detections
        )


class YoloVisionBackend:
    """Runtime YOLO backend that loads Ultralytics only when needed."""

    name = "ultralytics-yolov8"

    def __init__(
        self,
        model_path: str | Path,
        *,
        confidence_threshold: float = 0.25,
    ) -> None:
        self.model_path = Path(model_path)
        self.confidence_threshold = confidence_threshold
        self._model = None

    def is_ready(self) -> bool:
        return self.model_path.exists()

    def infer(self, frame: RuntimeFrame) -> Sequence[Detection]:
        if not self.is_ready():
            raise FileNotFoundError(
                f"YOLO model file not found at {self.model_path}. Train or place a model before runtime inference."
            )
        model = self._load_model()
        results = model.predict(frame.image, conf=self.confidence_threshold, verbose=False)
        return tuple(self._convert_results(results))

    def _load_model(self) -> Any:
        if self._model is not None:
            return self._model
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise InferenceDependencyError(
                "Ultralytics is not installed. Install it with `pip install ultralytics` to use the YOLO backend."
            ) from exc
        self._model = YOLO(str(self.model_path))
        return self._model

    def _convert_results(self, results: Sequence[Any]) -> list[Detection]:
        detections: list[Detection] = []
        for result in results:
            names = getattr(result, "names", {})
            boxes = getattr(result, "boxes", None)
            if boxes is None:
                continue
            cls_values = getattr(boxes, "cls", ())
            conf_values = getattr(boxes, "conf", ())
            xyxy_values = getattr(boxes, "xyxy", ())
            for cls_id, confidence, xyxy in zip(cls_values, conf_values, xyxy_values):
                class_index = int(_to_scalar(cls_id))
                coords = _to_list(xyxy)
                if len(coords) != 4:
                    continue
                detections.append(
                    Detection(
                        label=str(names.get(class_index, f"class_{class_index}")),
                        confidence=float(_to_scalar(confidence)),
                        bounding_box=BoundingBox(
                            x_min=int(coords[0]),
                            y_min=int(coords[1]),
                            x_max=int(coords[2]),
                            y_max=int(coords[3]),
                        ),
                        source=self.name,
                    )
                )
        return detections


def _to_scalar(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    return value


def _to_list(value: Any) -> list[Any]:
    if hasattr(value, "tolist"):
        converted = value.tolist()
        if isinstance(converted, list):
            return converted
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]
