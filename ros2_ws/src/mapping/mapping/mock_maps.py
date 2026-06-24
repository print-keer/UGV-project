from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class MockMap:
    name: str
    description: str
    start: Tuple[int, int]
    goal: Tuple[int, int]
    grid: List[List[int]]
    dynamic_obstacles: List[Tuple[int, int]] = field(default_factory=list)
    lidar_observations: List[List[Tuple[int, int]]] = field(default_factory=list)
    ultrasonic_observations: List[List[Tuple[int, int]]] = field(default_factory=list)


def load_mock_map(map_path: Path) -> MockMap:
    payload = json.loads(map_path.read_text(encoding="utf-8"))
    return MockMap(
        name=payload["name"],
        description=payload["description"],
        start=tuple(payload["start"]),
        goal=tuple(payload["goal"]),
        grid=payload["grid"],
        dynamic_obstacles=[tuple(cell) for cell in payload.get("dynamic_obstacles", [])],
        lidar_observations=[
            [tuple(cell) for cell in observation]
            for observation in payload.get("lidar_observations", [])
        ],
        ultrasonic_observations=[
            [tuple(cell) for cell in observation]
            for observation in payload.get("ultrasonic_observations", [])
        ],
    )


def load_all_mock_maps(maps_dir: Path) -> Dict[str, MockMap]:
    maps: Dict[str, MockMap] = {}
    for map_path in sorted(maps_dir.glob("*.json")):
        mock_map = load_mock_map(map_path)
        maps[mock_map.name] = mock_map
    return maps
