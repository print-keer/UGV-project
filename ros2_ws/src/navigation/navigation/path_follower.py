from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

GridCell = Tuple[int, int]


@dataclass
class NavigationReport:
    accepted: bool
    waypoint_count: int
    message: str
    waypoints: List[GridCell]


class PathFollower:
    """Placeholder path consumer for milestone one simulation flow."""

    def consume_path(self, path: List[GridCell]) -> NavigationReport:
        if not path:
            return NavigationReport(False, 0, "No path available for navigation.", [])
        return NavigationReport(
            accepted=True,
            waypoint_count=len(path),
            message="Path accepted by navigation layer.",
            waypoints=path,
        )

