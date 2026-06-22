from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BoundingBox:
    x_min: int
    y_min: int
    x_max: int
    y_max: int


@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float
    bounding_box: BoundingBox
    source: str


@dataclass(frozen=True)
class ThreatAssessment:
    highest_priority_label: str | None
    harmful_count: int
    harmless_count: int
    unknown_count: int
    alert_required: bool
    summary: str
