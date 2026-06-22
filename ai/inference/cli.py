from __future__ import annotations

import argparse
from pathlib import Path

from ai.inference.camera import load_image_frame
from ai.inference.pipeline import run_mock_inference, run_runtime_inference
from ai.threat_classifier.classifier import assess_detections


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="UGV Person 2 inference runner.")
    parser.add_argument(
        "--mode",
        choices=("mock", "image"),
        default="mock",
        help="Use mock frames or run inference on a single image.",
    )
    parser.add_argument(
        "--image-path",
        help="Image path for image mode.",
    )
    parser.add_argument(
        "--model-path",
        default="ai/models/best.pt",
        help="YOLO model path for image mode.",
    )
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.25,
        help="Confidence threshold passed to the YOLO backend.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.mode == "mock":
        results = run_mock_inference()
    else:
        if not args.image_path:
            raise SystemExit("--image-path is required when --mode image is used.")
        frame = load_image_frame(Path(args.image_path))
        results = run_runtime_inference(
            [frame],
            model_path=args.model_path,
            confidence_threshold=args.confidence_threshold,
        )

    for result in results:
        assessment = assess_detections(result.detections)
        print(
            {
                "frame_id": result.frame_id,
                "backend": result.backend_name,
                "detections": len(result.detections),
                "summary": assessment.summary,
            }
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
