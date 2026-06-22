from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare the MVRSD dataset for UGV training.")
    parser.add_argument(
        "--source-root",
        default="ai/dataset/raw/MVRSD_dataset/data",
        help="Source dataset root containing images/ and labels/ directories.",
    )
    parser.add_argument(
        "--binary-output-root",
        default="ai/dataset/processed/mvrsd_binary",
        help="Output root for the binary harmful-only dataset.",
    )
    return parser


def prepare_mvrsd_dataset(source_root: Path, binary_output_root: Path) -> dict[str, int]:
    if not source_root.exists():
        raise FileNotFoundError(f"MVRSD source root not found at {source_root}.")

    class_names = _read_lines(source_root / "labels" / "classes.txt")
    if not class_names:
        raise RuntimeError("No class names found in the MVRSD classes file.")

    _reset_directory(binary_output_root)

    image_counts: dict[str, int] = {}
    label_counts: dict[str, int] = {}
    object_counts: dict[str, int] = {}

    for split in ("train", "val"):
        source_images = source_root / "images" / split
        source_labels = source_root / "labels" / split
        target_images = binary_output_root / "images" / split
        target_labels = binary_output_root / "labels" / split
        target_images.mkdir(parents=True, exist_ok=True)
        target_labels.mkdir(parents=True, exist_ok=True)

        image_counts[split] = _copy_files(source_images, target_images)
        label_counts[split], object_counts[split] = _convert_split_labels(
            source_labels=source_labels,
            target_labels=target_labels,
        )

    (binary_output_root / "data.yaml").write_text(
        "\n".join(
            [
                f"path: {binary_output_root.resolve().as_posix()}",
                "train: images/train",
                "val: images/val",
                "",
                "names:",
                "  0: harmful",
                "",
            ]
        ),
        encoding="utf-8",
    )

    return {
        "source_classes": len(class_names),
        "train_images": image_counts["train"],
        "val_images": image_counts["val"],
        "train_label_files": label_counts["train"],
        "val_label_files": label_counts["val"],
        "train_objects": object_counts["train"],
        "val_objects": object_counts["val"],
    }


def _read_lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _reset_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def _copy_files(source_dir: Path, target_dir: Path) -> int:
    count = 0
    for source_file in sorted(source_dir.iterdir()):
        if source_file.is_file():
            shutil.copy2(source_file, target_dir / source_file.name)
            count += 1
    return count


def _convert_split_labels(*, source_labels: Path, target_labels: Path) -> tuple[int, int]:
    file_count = 0
    object_count = 0
    for source_label in sorted(source_labels.glob("*.txt")):
        converted_lines: list[str] = []
        for line in source_label.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            parts = stripped.split()
            if len(parts) != 5:
                raise RuntimeError(f"Unexpected YOLO label format in {source_label}: {stripped}")
            converted_lines.append("0 " + " ".join(parts[1:]))
        (target_labels / source_label.name).write_text(
            "\n".join(converted_lines) + ("\n" if converted_lines else ""),
            encoding="utf-8",
        )
        file_count += 1
        object_count += len(converted_lines)
    return file_count, object_count


def main() -> int:
    args = build_parser().parse_args()
    summary = prepare_mvrsd_dataset(
        source_root=Path(args.source_root),
        binary_output_root=Path(args.binary_output_root),
    )
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
