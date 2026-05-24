from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Sequence, Tuple

GridCell = Tuple[int, int]
Grid = Sequence[Sequence[int]]
EdgeCostFn = Callable[[GridCell, int], float]


@dataclass(frozen=True)
class PlannerConfig:
    free_value: int = 0
    obstacle_value: int = 1
    unknown_value: int = 2
    allow_unknown_cells: bool = True
    straight_step_cost: float = 1.0
    unknown_cell_penalty: float = 4.0


@dataclass
class PlanResult:
    path_found: bool
    path: List[GridCell] = field(default_factory=list)
    total_cost: float = 0.0
    visited_nodes: int = 0
    message: str = ""

