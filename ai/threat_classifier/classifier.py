from __future__ import annotations

from collections.abc import Sequence

from ai.threat_classifier.types import Detection, ThreatAssessment

HARMFUL_LABELS = frozenset({"harmful", "smv", "lmv", "afv", "cv", "mcv"})
HARMLESS_LABELS = frozenset({"harmless"})


def normalize_label(label: str) -> str:
    return label.strip().lower().replace(" ", "_")


def classify_label(label: str) -> str:
    normalized = normalize_label(label)
    if normalized in HARMFUL_LABELS:
        return "harmful"
    if normalized in HARMLESS_LABELS:
        return "harmless"
    return "unknown"


def assess_detections(detections: Sequence[Detection]) -> ThreatAssessment:
    harmful_count = 0
    harmless_count = 0
    unknown_count = 0
    highest_priority_label: str | None = None

    for detection in detections:
        category = classify_label(detection.label)
        if category == "harmful":
            harmful_count += 1
            highest_priority_label = "harmful"
        elif category == "harmless":
            harmless_count += 1
            if highest_priority_label is None:
                highest_priority_label = "harmless"
        else:
            unknown_count += 1
            if highest_priority_label is None:
                highest_priority_label = "unknown"

    alert_required = harmful_count > 0
    summary = build_summary(
        harmful_count=harmful_count,
        harmless_count=harmless_count,
        unknown_count=unknown_count,
        alert_required=alert_required,
    )
    return ThreatAssessment(
        highest_priority_label=highest_priority_label,
        harmful_count=harmful_count,
        harmless_count=harmless_count,
        unknown_count=unknown_count,
        alert_required=alert_required,
        summary=summary,
    )


def build_summary(
    *,
    harmful_count: int,
    harmless_count: int,
    unknown_count: int,
    alert_required: bool,
) -> str:
    if harmful_count == harmless_count == unknown_count == 0:
        return "No detections were produced for this frame."
    if alert_required:
        return (
            f"[ALERT] harmful={harmful_count} harmless={harmless_count} "
            f"unknown={unknown_count}. Mission should continue with threat logging."
        )
    return (
        f"[CLEAR] harmful={harmful_count} harmless={harmless_count} "
        f"unknown={unknown_count}. Navigation can continue without alert escalation."
    )
