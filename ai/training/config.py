from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TrainingConfig:
    model: str = "yolov8n.pt"
    data_config: str = "ai/dataset/data.yaml"
    epochs: int = 100
    image_size: int = 640
    project_dir: str = "ai/models/runs"
    run_name: str = "binary_threat_detection"
    output_model_path: str = "ai/models/best.pt"

    def build_command(self) -> list[str]:
        return [
            "yolo",
            "task=detect",
            "mode=train",
            f"model={self.model}",
            f"data={self.data_config}",
            f"epochs={self.epochs}",
            f"imgsz={self.image_size}",
            f"project={self.project_dir}",
            f"name={self.run_name}",
        ]

    def validate_paths(self, repo_root: Path) -> None:
        data_path = repo_root / self.data_config
        if not data_path.exists():
            raise FileNotFoundError(
                f"Training data config not found at {data_path}. Create it before launching training."
            )

    def resolved_output_model_path(self, repo_root: Path) -> Path:
        return repo_root / self.output_model_path
