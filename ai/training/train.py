from __future__ import annotations

import argparse
import shlex
from pathlib import Path

from ai.training.config import TrainingConfig


DATASET_PRESETS = {
    "mvrsd-binary": TrainingConfig(
        data_config="ai/dataset/processed/mvrsd_binary/data.yaml",
        run_name="mvrsd_binary_harmful",
        output_model_path="ai/models/mvrsd_binary_best.pt",
    ),
    "mvrsd-multiclass": TrainingConfig(
        data_config="ai/dataset/mvrsd_multiclass.yaml",
        run_name="mvrsd_multiclass_vehicle_types",
        output_model_path="ai/models/mvrsd_multiclass_best.pt",
    ),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build YOLO training commands for UGV datasets.")
    parser.add_argument(
        "--preset",
        choices=sorted(DATASET_PRESETS),
        default="mvrsd-binary",
        help="Dataset preset to target.",
    )
    parser.add_argument("--epochs", type=int, help="Override epoch count.")
    parser.add_argument("--imgsz", type=int, help="Override image size.")
    parser.add_argument(
        "--print-command-only",
        action="store_true",
        help="Print the YOLO command without executing it.",
    )
    return parser


def build_config(args: argparse.Namespace) -> TrainingConfig:
    config = DATASET_PRESETS[args.preset]
    if args.epochs is not None:
        config = TrainingConfig(
            model=config.model,
            data_config=config.data_config,
            epochs=args.epochs,
            image_size=config.image_size if args.imgsz is None else args.imgsz,
            project_dir=config.project_dir,
            run_name=config.run_name,
            output_model_path=config.output_model_path,
        )
    elif args.imgsz is not None:
        config = TrainingConfig(
            model=config.model,
            data_config=config.data_config,
            epochs=config.epochs,
            image_size=args.imgsz,
            project_dir=config.project_dir,
            run_name=config.run_name,
            output_model_path=config.output_model_path,
        )
    return config


def main() -> int:
    args = build_parser().parse_args()
    config = build_config(args)
    repo_root = Path(__file__).resolve().parents[2]
    config.validate_paths(repo_root)
    command = config.build_command()
    print(shlex.join(command))
    if args.print_command_only:
        return 0
    raise SystemExit(
        "This helper currently prints the YOLO command only. Run the printed command in an environment with ultralytics installed."
    )


if __name__ == "__main__":
    raise SystemExit(main())
